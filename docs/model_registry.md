# Model Registry Workflow

This document describes how to identify, version, and promote trained Mastermind RL models using the W&B Model Registry.

## 1. Identify the Best Run

After a sweep completes, open the W&B project dashboard:

```
https://wandb.ai/<entity>/<project>/sweeps/<sweep_id>
```

Sort the runs table by `eval/avg_guesses` ascending. The top row is the best run. Note its **run name** (e.g. `sleek-dream-42`) and **run ID**.

Alternatively, query via the CLI:

```bash
wandb sweep --project mastermind-rl <sweep_id>
```

## 2. Log the Model as an Artifact

The best run's model is saved locally at `outputs/sweep/<run_name>/model.zip`. Log it to the W&B artifact store:

```bash
cd /path/to/MastermindAI

wandb artifact put \
  --name mastermind-rl/mastermind-model \
  --type model \
  --description "Best sweep run: <run_name>, avg_guesses=<value>" \
  outputs/sweep/<run_name>/model.zip
```

Or programmatically:

```python
import wandb

run = wandb.init(project="mastermind-rl", job_type="registry")
artifact = wandb.Artifact("mastermind-model", type="model")
artifact.add_file("outputs/sweep/<run_name>/model.zip")
run.log_artifact(artifact)
run.finish()
```

Each call creates a new version automatically (`v0`, `v1`, `v2`, ...).

## 3. Tag a Version

Add a human-readable alias to the artifact version in the W&B UI:

1. Navigate to **Artifacts** > **mastermind-model**
2. Select the version (e.g. `v2`)
3. Click **Add alias** and type `v1`, `v2`, etc. to match your release numbering

Or via CLI:

```bash
wandb artifact put \
  --name mastermind-rl/mastermind-model:v1 \
  --type model \
  outputs/sweep/<run_name>/model.zip
```

## 4. Promote to `prod`

The `prod` alias marks the model that the production API loads. Only one version should carry this alias at a time.

**Via W&B UI:**

1. Navigate to **Artifacts** > **mastermind-model**
2. Select the version to promote
3. Click **Add alias** and type `prod`
4. Remove the `prod` alias from any previous version

**Via Python:**

```python
import wandb

api = wandb.Api()
artifact = api.artifact("mastermind-rl/mastermind-model:v2")
artifact.aliases.append("prod")
artifact.save()
```

## 5. What `prod` Means

The API service (Phase 8) loads the model tagged `prod` at startup:

```python
artifact = run.use_artifact("mastermind-rl/mastermind-model:prod")
model_dir = artifact.download()
model = MaskablePPO.load(os.path.join(model_dir, "model"))
```

This decouples deployment from training — new models can be trained and versioned without touching the API code. Promoting a new version to `prod` is a single alias change that takes effect on the next API restart.
