# Training Provenance

This folder preserves the surviving evidence for the original LoRA training runs.

## Preserved artifacts

### Monet style

- `configs/monet_last_20231129-043745.json`

Preserved settings visible in the JSON include:

- base model: `runwayml/stable-diffusion-v1-5`
- resolution: `1024,1024`
- LoRA rank (`network_dim`): `8`
- LoRA alpha (`network_alpha`): `1`
- train batch size: `16`
- text encoder LR: `5e-05`
- U-Net LR: `0.0001`
- optimizer: `AdamW`
- epochs: `100`
- xformers enabled

### Painting / animate-style run

- `configs/painting_v1_20231211-043052.json`
- `logs/painting_script_caption.txt`
- `logs/animation_training_log.txt`

Preserved settings include:

- base model: `runwayml/stable-diffusion-v1-5`
- resolution: `512, 512`
- LoRA rank (`network_dim`): `25`
- LoRA alpha (`network_alpha`): `25`
- train batch size: `16`
- text encoder LR: `5e-05`
- U-Net LR: `0.0001`
- optimizer: `AdamW`
- max train steps: `93750`
- lr warmup steps: `9375`
- xformers enabled
- preserved kohya launch command in `painting_script_caption.txt`

## Known unknowns

- exact training seed: **Unknown**
- exact dataset snapshot: **Unknown**
- exact folder state at train time: **Unknown**
- exact 1:1 mapping between local `painting_v1` artifacts and the current public HF checkpoint: **Not sure**

## Policy for this repository

The app repository should **document** training provenance, not pretend to fully reproduce it.
