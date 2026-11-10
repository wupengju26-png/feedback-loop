"""Check local provenance, evidence references, and completeness; never judge semantics."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "counsel-10"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(value, pointer):
    if not pointer.startswith("/"):
        raise ValueError("Evidence pointer must start with /")
    for component in pointer[1:].split("/"):
        key = component.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def check(partial=False):
    manifest = read(BASE / "manifest.json")
    errors = []
    totals = dict(inputs=0, feedback=0, findings=0, evidence=0, reviews=0)
    for record in manifest["samples"]:
        name = record["sample_id"]
        path = BASE / record["input_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["input_sha256"]:
            errors.append(f"{name}: input hash mismatch")
        source = read(path)
        totals["inputs"] += 1
        target = BASE / "feedback" / f"{name}.json"
        if not target.exists():
            if not partial:
                errors.append(f"{name}: missing feedback")
            continue
        candidate = read(target)
        totals["feedback"] += 1
        if candidate["trace_id"] != source["trace-id"]:
            errors.append(f"{name}: wrong trace id")
        if candidate["status"] not in {"issues_found", "no_supported_issue", "insufficient_evidence"}:
            errors.append(f"{name}: invalid status")
        if bool(candidate["findings"]) != (candidate["status"] == "issues_found"):
            errors.append(f"{name}: status disagrees with findings")
        ids = set()
        for finding in candidate["findings"]:
            totals["findings"] += 1
            if finding["id"] in ids:
                errors.append(f"{name}: duplicate finding id")
            ids.add(finding["id"])
            for field in ("problem", "explanation", "suggestion", "evidence"):
                if not finding.get(field):
                    errors.append(f"{name}/{finding['id']}: empty {field}")
            position = finding["message_index"]
            if type(position) is not int or not 0 <= position < len(source["trajectory"]):
                errors.append(f"{name}/{finding['id']}: invalid finding position")
            for evidence in finding["evidence"]:
                totals["evidence"] += 1
                try:
                    index = evidence["message_index"]
                    if type(index) is not int or not 0 <= index < len(source["trajectory"]):
                        raise ValueError("Invalid evidence position")
                    value = resolve(source["trajectory"][index], evidence["pointer"])
                    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
                    if not evidence["quote"] or evidence["quote"] not in text:
                        raise ValueError("Quote is not an exact substring")
                except (KeyError, IndexError, TypeError, ValueError) as exc:
                    errors.append(f"{name}/{finding['id']}: {exc}")
        review_path = BASE / "reviews" / f"{name}.json"
        if review_path.exists():
            review = read(review_path)
            totals["reviews"] += 1
            if review.get("trace_id") != source["trace-id"]:
                errors.append(f"{name}: wrong review trace id")
            if {f["finding_id"] for f in review["finding_reviews"]} != ids:
                errors.append(f"{name}: review does not cover each candidate finding")
            valid_annotation_ids = {r["meta-annotation-id"] for r in read(BASE / "reference" / f"{name}.json")}
            for finding_review in review["finding_reviews"]:
                if finding_review["verdict"] not in {"supported", "partially_supported", "unsupported", "uncertain"}:
                    errors.append(f"{name}: invalid review verdict")
                for annotation_id in finding_review.get("related_annotation_ids", []):
                    if annotation_id not in valid_annotation_ids:
                        errors.append(f"{name}: unknown reference annotation id {annotation_id}")
        elif not partial:
            errors.append(f"{name}: missing review")

    receipt_path = BASE / "generation-receipt.json"
    if receipt_path.exists():
        receipt = read(receipt_path)
        expected_files = {"prompt.txt"} | {f"feedback/{r['sample_id']}.json" for r in manifest["samples"]}
        if not partial and (not receipt.get("finalized") or {e["file"] for e in receipt["files"]} != expected_files):
            errors.append("Generation receipt does not freeze the prompt and every candidate")
        for entry in receipt["files"]:
            if hashlib.sha256((BASE / entry["file"]).read_bytes()).hexdigest() != entry["sha256"]:
                errors.append(f"Generation receipt changed: {entry['file']}")
    elif not partial:
        errors.append("Missing generation receipt")
    print(json.dumps(dict(totals=totals, errors=errors,
                          scope="Structural integrity and exact quotations only; no semantic correctness score"), ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partial", action="store_true", help="Allow candidates and reviews that are not yet written")
    args = parser.parse_args()
    raise SystemExit(check(args.partial))
