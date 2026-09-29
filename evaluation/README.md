# Evaluation

This directory contains:

- **questions.json**: Test question set (planned for Day 7)
- **results.json**: Measured evaluation results (planned for Day 7)

The evaluation uses Recall@K as the primary metric.

## Planned Evaluation Dataset

Approximately 30–50 questions about the indexed codebase.

Each question will record:
- The question text
- Expected relevant files
- Retrieved top-K results
- Whether relevant evidence was found
- Answer correctness
- Groundedness in the retrieved context

No results exist yet — they will be measured after the pipeline is fully implemented.
