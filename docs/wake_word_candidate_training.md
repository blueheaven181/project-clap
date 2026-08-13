# Versioned Wake-Word Candidate Training

This workflow keeps Project CLAP's runtime and current wake model unchanged
until a separately tested candidate is explicitly approved.

## Isolation

- Runtime environment: `.venv` on Python 3.13.
- Training environment (local, short-path, and ignored):
  `.wake-env` on Python 3.10. The short path avoids Windows' legacy path
  limit in TensorFlow's deeply nested header files.
- Dependency manifest: `config/wake_word_training_requirements.txt`.
- Never install training packages into `.venv`.
- Never write training output directly into `models/wake_words`.

## Private Inputs

- Positive session:
  `recordings/wake_word_training/positive/20260807_041003`
- Negative session:
  `recordings/wake_word_training/negative/20260807_041603`

The recordings remain local and Git-ignored. Training requires separate
permission to read and process their audio contents.

## Run Layout

Each approved run receives a new immutable run identifier:

```text
recordings/wake_word_training/training_runs/<run-id>/
  config/
  manifests/
  features/
  checkpoints/
  candidate/
    hey_Clap_candidate_<run-id>.onnx
    hey_Clap_candidate_<run-id>.onnx.data  (only if exporter creates it)
  metrics/
  environment/
    requirements-resolved.txt
  hashes.sha256
```

The entire run directory is ignored by Git. A failed or weak run is retained
for comparison or removed only after explicit approval.

## Candidate Gate

1. Preserve and re-check the SHA-256 hashes of the current model pair.
2. Split personal recordings so validation clips are never used for fitting.
3. Generate or obtain the broader synthetic-positive, negative-background,
   noise, and room-impulse data required by OpenWakeWord.
4. Train and export only into the run's `candidate` directory.
5. Run standalone A/B scoring against the current and candidate models.
6. Require improved normal-distance recall without a regression in ordinary
   speech or nearby-speaker false activations.
7. Copy a successful model into a new versioned production-candidate path only
   after explicit approval. Never overwrite `hey_Clap.onnx` or its data file.
8. Keep double-clap activation available throughout evaluation and rollout.

## Rollback Baseline

- `hey_Clap.onnx`:
  `F6B1544F776D225884CF196D5E25DAD234228736DED1931AA97B9745E38A6901`
- `hey_Clap.onnx.data`:
  `CFBF4F6513496765D8948C42FEB0FB9EFA94A38A7853623F2E6B8A25FB1ED256`

Production continues using this pair unless a later, explicit selection change
is approved. Rollback means selecting this unchanged pair again.

## Approvals Still Required

Before dependency installation:

- Approve large Python/ML package downloads and disk use.

Before data preparation or training:

- Approve local reading and processing of the private WAV recordings.
- Approve any synthetic speech models or public background datasets and their
  download size/licenses.
- Approve the exact training configuration and run identifier.

Before production use:

- Review A/B metrics and approve a versioned candidate selection.
