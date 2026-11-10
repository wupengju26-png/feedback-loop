"""Fetch a small, reproducible Counsel sample using only Python's standard library."""

import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "experiments" / "counsel-10"
DATASET = "AtlaAI/counsel"
REVISION = "97801e8a9dfece812225035815c100a9ff21f5a4"
SEED = "feedback-loop-counsel-10-v1"


def fetch(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return response.read(), response.headers.get("x-revision")
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_page(config, offset, length=25):
    query = urllib.parse.urlencode(dict(dataset=DATASET, config=config, split="all", offset=offset, length=length))
    url = "https://datasets-server.huggingface.co/rows?" + query
    body, revision = fetch(url)
    if revision != REVISION:
        raise RuntimeError(f"Unexpected source revision: {revision}")
    data = json.loads(body)
    if any(row.get("truncated_cells") for row in data["rows"]):
        raise RuntimeError(f"Truncated cells in {url}")
    return data


def all_rows(config):
    first = get_page(config, 0)
    total = first["num_rows_total"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rest = list(pool.map(lambda offset: get_page(config, offset), range(25, total, 25)))
    rows = [row for page in [first, *rest] for row in page["rows"]]
    if len(rows) != total or len({row["row_idx"] for row in rows}) != total:
        raise RuntimeError("Incomplete source pagination")
    return rows


def main():
    metadata, _ = fetch("https://huggingface.co/api/datasets/" + DATASET)
    if json.loads(metadata)["sha"] != REVISION:
        raise RuntimeError("Source has changed; review the pinned revision before sampling")
    trajectories = all_rows("trajectories")
    selected = []
    for environment in sorted({r["row"]["environment"] for r in trajectories}):
        # Exclude the first 40 viewer rows: some were exposed with labels during research.
        eligible = [r for r in trajectories if r["row_idx"] >= 40 and r["row"]["environment"] == environment]
        eligible.sort(key=lambda r: hashlib.sha256((SEED + ":" + r["row"]["trace-id"]).encode()).hexdigest())
        selected.extend(eligible[:5])
    if len(selected) != 10:
        raise RuntimeError("Expected five examples in each of two environments")

    records = []
    for number, wrapped in enumerate(selected, 1):
        row = wrapped["row"]
        name = f"{number:02d}-{row['trace-id']}"
        path = DEST / "inputs" / f"{name}.json"
        write_json(path, row)
        view = [f"# {name}", f"Environment: {row['environment']}",
                "Message numbers below are zero-based positions in the trajectory array.",
                "This file contains trajectory data only; no critique or meta-annotation."]
        for index, message in enumerate(row["trajectory"]):
            view.extend([f"\n## Message {index}", "```json", json.dumps(message, ensure_ascii=False, indent=2), "```"])
        (DEST / "inputs" / f"{name}.md").write_text("\n".join(view) + "\n", encoding="utf-8")
        records.append(dict(sample_id=name, trace_id=row["trace-id"], environment=row["environment"],
                            source_row_index=wrapped["row_idx"], messages=len(row["trajectory"]),
                            input_file=path.relative_to(DEST).as_posix(),
                            input_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))

    # Stored separately. Feedback authors must finish their outputs before reading this directory.
    annotations = all_rows("meta-annotations")
    by_trace = {}
    for wrapped in annotations:
        row = wrapped["row"]
        by_trace.setdefault(row["trace-id"], []).append(row)
    for record in records:
        write_json(DEST / "reference" / (record["sample_id"] + ".json"), by_trace.get(record["trace_id"], []))

    readme, _ = fetch(f"https://huggingface.co/datasets/{DATASET}/raw/{REVISION}/README.md")
    (DEST / "reference" / "upstream-dataset-card.md").write_bytes(readme)
    write_json(DEST / "manifest.json", dict(
        dataset=DATASET, dataset_url="https://huggingface.co/datasets/" + DATASET,
        revision=REVISION, source_license="MIT (upstream dataset card)",
        retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        selection=dict(seed=SEED, method="SHA256(seed + ':' + trace-id), ascending, five per environment",
                       exclude_source_rows_below=40, rationale="Avoid viewer rows whose annotations were exposed during earlier research; selection does not use labels"),
        provenance="Hugging Face rows API; every response x-revision checked against pinned revision; truncated cells rejected",
        source_totals=dict(trajectories=len(trajectories), meta_annotations=len(annotations)),
        samples=records))
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
