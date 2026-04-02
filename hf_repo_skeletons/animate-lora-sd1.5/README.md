---
pipeline_tag: text-to-image
library_name: diffusers
license: mit
base_model: runwayml/stable-diffusion-v1-5
tags:
  - stable-diffusion
  - stable-diffusion-diffusers
  - lora
  - diffusers
  - image-generation
---

# animate-lora-sd1.5

LoRA adapter for cinematic anime-style landscape generation on top of **Stable Diffusion 1.5**.

## Model summary

- **Base model**: `runwayml/stable-diffusion-v1-5`
- **Trigger words**: `landscape`, `sms landscape`
- **Adapter file**: `animate_v1-000005.safetensors`

## Preserved training evidence

Preserved local artifacts suggest the original training run used:

- resolution: `512, 512`
- network_dim: `25`
- network_alpha: `25`
- train_batch_size: `16`
- text_encoder_lr: `5e-05`
- unet_lr: `0.0001`
- optimizer: `AdamW`
- max_train_steps: `93750`
- lr_warmup_steps: `9375`
- xformers enabled

A preserved caption / training script and a preserved JSON config are included as provenance files.

## Known unknowns

The exact mapping between the preserved local `painting_v1` artifacts and this public checkpoint is **Not sure**.
Exact seed and exact dataset snapshot are **Unknown**.

## Diffusers usage

```python
import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

pipe.load_lora_weights(
    "J-YOON/animate-lora-sd1.5",
    weight_name="animate_v1-000005.safetensors",
)

prompt = "sms landscape, evening sky over a quiet city, cinematic diary illustration"
image = pipe(prompt, num_inference_steps=30, guidance_scale=7.0).images[0]
image.save("animate_example.png")
```

## Limitations

- This repository is for inference-oriented sharing.
- It does not ship the entire original training framework.
- Exact end-to-end reproduction is **Not sure**.

## Gallery

<Gallery>
![Example 1](./images/example_01.png)
![Example 2](./images/example_02.png)
</Gallery>
