# Hugging Face Model Repo Cleanup

## Goal

Turn each model repo into a **clean adapter release** instead of a mixed training dump.

## Keep in the public model repo

- `README.md` (model card)
- `images/` (example outputs)
- the **LoRA weight file**
- optional small metadata files such as preserved training JSON or notes

## Remove from the public model repo

If the repo is meant for inference and sharing, do **not** keep large training-state artifacts publicly unless you have a specific reason.

Typical removal list:

- `optimizer.bin`
- `random_states_0.pkl`
- `scaler.pt`
- `scheduler.bin`
- `pytorch_model.bin`
- `pytorch_model_1.bin`
- `pytorch_model_2.bin`

## Recommended public file layout

### monet repo

```text
lora-monet-sd1.5/
├─ README.md
├─ images/
│  ├─ example_01.png
│  ├─ example_02.png
│  └─ ...
├─ pytorch_lora_weights.safetensors
└─ metadata/
   └─ monet_last_20231129-043745.json
```

### animate repo

```text
animate-lora-sd1.5/
├─ README.md
├─ images/
│  ├─ example_01.png
│  ├─ example_02.png
│  └─ ...
├─ animate_v1-000005.safetensors
└─ metadata/
   ├─ painting_v1_20231211-043052.json
   └─ painting_script_caption.txt
```

## Filename policy

Two safe options:

1. **Keep the current filename** and load it with `weight_name=...`.
2. Rename to `pytorch_lora_weights.safetensors` for consistency.

If backward compatibility matters, option 1 is safer.

## Model card sections you should add

- model summary
- base model
- trigger words
- intended use
- preserved training settings
- known unknowns
- usage example
- limitations
- example gallery
