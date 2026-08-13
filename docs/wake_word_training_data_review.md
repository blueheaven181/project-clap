# Wake-Word Training Data Review

Review date: 2026-08-11

No external training data was downloaded during this review.

## Prepared Local Run

- Run ID: `wake-candidate-20260811-224346`
- Clean positives: 20
- Ordinary-speech negatives: 20
- Speaker-playback negatives: 20
- Deterministic split: 48 training, 12 held-out validation
- Local run path:
  `recordings/wake_word_training/training_runs/wake-candidate-20260811-224346`

The run and all personal recordings are Git-ignored.

## Official OpenWakeWord 0.6 Baseline

The official example configuration recommends:

- At least 20,000 generated positive samples; 100,000 or more may perform
  better.
- 2,000 generated positive validation samples.
- Piper Sample Generator for synthetic speech.
- Room impulse responses for acoustic augmentation.
- Background audio for augmentation.
- Precomputed general negative features.
- A separate false-positive validation feature set.

## Proposed Downloads

### 1. General negative features

- File: `openwakeword_features_ACAV100M_2000_hrs_16bit.npy`
- Size: approximately 17.3 GB
- Contents: precomputed features representing about 2,000 hours of diverse
  multilingual speech, noise, music, and real-world audio.
- License: CC BY-NC-SA 4.0.
- Purpose: broad negative training coverage.

### 2. False-positive validation features

- File: `validation_set_features.npy`
- Size: approximately 185 MB
- Contents: precomputed features representing about 11 hours of speech,
  noise, and music.
- License: CC BY-NC-SA 4.0 as distributed in the feature dataset.
- Purpose: estimate false activations independently of training batches.

### 3. Piper synthetic-speech voice

- File: `en_US-libritts_r-medium.onnx` plus JSON configuration
- Size: approximately 78.6 MB plus a small JSON file.
- Repository license: MIT.
- Purpose: generate many varied `Hey CLAP` positive examples locally.

### 4. Piper Sample Generator

- Source: `rhasspy/piper-sample-generator`
- Repository license: MIT.
- Purpose: generate and augment positive speech samples.
- Expected source/package size: small compared with model/data files.

### 5. MIT environmental impulse responses

- Size: approximately 8.38 MB, 270 listed rows/files.
- License: listed as unknown by the dataset host.
- Purpose: simulate room echo and far-field microphone conditions.
- Recommendation: do not download or use until licensing is clarified, or
  substitute a clearly licensed RIR collection.

## Storage Budget

Core listed downloads total about 17.6 GB before generated clips, extracted
features, checkpoints, caches, and candidate artifacts. Reserve at least
35-45 GB for a practical run. Approximately 97 GB was free before these
downloads, so local capacity is adequate if caches are managed.

## Licensing Decision

The CC BY-NC-SA 4.0 feature data is reasonable for Marc's private,
noncommercial assistant. It may constrain redistribution or commercial use of
the resulting model. Keep attribution and provenance records with every run.

If future Project CLAP packaging is distributed commercially, use a separate
training run based only on datasets with commercial-compatible licenses.

## Recommended Approval Boundary

For the current private/noncommercial candidate, approve only:

1. Piper Sample Generator and the MIT-licensed LibriTTS-R Piper voice.
2. The 17.3 GB CC BY-NC-SA general negative feature file.
3. The 185 MB CC BY-NC-SA false-positive validation file.

Do not approve the unknown-license RIR dataset yet. Do not begin training as
part of the download step. Verify sizes and hashes after download, then prepare
the exact versioned YAML configuration for separate approval.

