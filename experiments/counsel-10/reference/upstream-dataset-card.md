---
dataset_info:
- config_name: meta-annotations
  features:
  - name: meta-annotation-id
    dtype: string
  - name: trace-id
    dtype: string
  - name: utterance-idx
    dtype: int64
  - name: judge-model
    dtype: string
  - name: judge-critique
    dtype: string
  - name: meta-judgement
    dtype: string
  - name: meta-comment
    dtype: string
  splits:
  - name: all
    num_bytes: 432489
    num_examples: 1131
  download_size: 187929
  dataset_size: 432489
- config_name: trajectories
  features:
  - name: trace-id
    dtype: string
  - name: environment
    dtype: string
  - name: agent-model
    dtype: string
  - name: trajectory
    list:
    - name: content
      dtype: string
    - name: finish_reason
      dtype: string
    - name: index
      dtype: int64
    - name: message
      struct:
      - name: content
        dtype: string
      - name: tool_calls
        list:
        - name: function
          struct:
          - name: arguments
            dtype: string
          - name: name
            dtype: string
        - name: id
          dtype: string
        - name: type
          dtype: string
    - name: role
      dtype: string
    - name: tool_calls
      list:
      - name: function
        struct:
        - name: arguments
          dtype: string
        - name: name
          dtype: string
      - name: id
        dtype: string
      - name: type
        dtype: string
    - name: tools
      list:
      - name: function
        struct:
        - name: description
          dtype: string
        - name: name
          dtype: string
        - name: parameters
          struct:
          - name: properties
            struct:
            - name: address1
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: address2
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: city
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: country
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: email
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: expression
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: first_name
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: item_ids
              struct:
              - name: description
                dtype: string
              - name: items
                struct:
                - name: type
                  dtype: string
              - name: type
                dtype: string
            - name: last_name
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: new_item_ids
              struct:
              - name: description
                dtype: string
              - name: items
                struct:
                - name: type
                  dtype: string
              - name: type
                dtype: string
            - name: order_id
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: payment_method_id
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: product_id
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: reason
              struct:
              - name: description
                dtype: string
              - name: enum
                list: string
              - name: type
                dtype: string
            - name: state
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: summary
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: thought
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: user_id
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
            - name: zip
              struct:
              - name: description
                dtype: string
              - name: type
                dtype: string
          - name: required
            list: string
          - name: type
            dtype: string
      - name: type
        dtype: string
  splits:
  - name: all
    num_bytes: 5815490
    num_examples: 225
  download_size: 927831
  dataset_size: 5815490
configs:
- config_name: meta-annotations
  data_files:
  - split: all
    path: meta-annotations/all-*
- config_name: trajectories
  data_files:
  - split: all
    path: trajectories/all-*
language:
- en
pretty_name: Counsel
size_categories:
- n<1K
license: mit
---

# Counsel Dataset Card

Counsel is the first dataset to provide human meta-evaluations of LLM-as-a-Judge (LLMJ) critiques on agentic task execution. It addresses a critical gap: while LLMJ critiques are essential for diagnosing and improving agentic systems, their accuracy and reliability have rarely been systematically evaluated—until now. Counsel empowers researchers and practitioners to benchmark, refine, and trust LLMJ critiques by offering high-quality, human-validated annotations over real-world agentic traces.

## Dataset Details

Counsel includes 225 unique agent execution traces, spanning two widely used real-world agentic benchmarks:

- ⁠TauBench (Retail): a customer support dataset. This makes up 185 traces
- ⁠DACode: a code generation and debugging dataset. This makes up 40 traces.

We generated the execution traces by two two agent models with distinct reasoning styles: GPT-OSS-20B (medium reasoning) and Qwen3-235B-A22B-Instruct-2507 (no reasoning).

The dataset contains process-level (span) judgements by three judge models - Qwen-3, GPT-OSS-2B:low and GPT-OSS-20B:high - with the corresponding human-annotated meta-judgement. Each judge critiques every span of the trace, but only those flagged to have errors are meta-judge by humans. These meta-judgements assess both the location and reasoning quality of each judge model critique:

- **Spot On:** Both the error location and the reasoning/critique are correct
- **Poor Reasoning but Right Location:** The judge correctly identified where an error occurred, but provided incorrect or inadequate reasoning for why it is an error
- **Should Not Have Flagged:** The judge incorrectly flagged this location as containing an error (both location and reasoning are wrong

Annotators may optionally provide a meta-comment.

Along with the meta-evaluation, we also provide the full 225 agent trajectories.

## Annotation Quality

Each annotation has been labeled by three human annotators, each a skilled data scientist with over 10 years of experience in data science and NLP, obtaining high IAA (Krippendorff’s alpha 0.78). This dataset can be used to improve judges themselves, helping to optimise objectives that directly incentivise correct error localisation and faithful rationale.

## Dataset Source

### Paper

Counsel: A Meta-Evaluation Dataset for Agentic Tasks

- arXiv: https://arxiv.org/abs/2606.21627
- Hugging Face paper page: https://huggingface.co/papers/2606.21627

## Citation

```bibtex
@misc{pisupati2026counsel,
  title = {Counsel: A Meta-Evaluation Dataset for Agentic Tasks},
  author = {Pisupati, Sashank and Broomfield, Henry and Choi, Eujong and Calvi, Antonia and Wang, Charlie and Engeler, Roman and Bartolo, Max and Lewis, Patrick},
  year = {2026},
  eprint = {2606.21627},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  url = {https://arxiv.org/abs/2606.21627}
}
```
