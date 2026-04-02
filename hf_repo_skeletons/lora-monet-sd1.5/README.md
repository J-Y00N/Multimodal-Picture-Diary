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

# lora-monet-sd1.5

LoRA adapter for Monet-style image generation on top of **Stable Diffusion 1.5**.

## Model summary

- **Base model**: `runwayml/stable-diffusion-v1-5`
- **Trigger word**: `msl monet`
- **Adapter file**: `pytorch_lora_weights.safetensors`

## Intended use

This adapter is intended for stylized artistic image generation and diary-style illustration experiments.

## Preserved training settings

The following settings are preserved from the surviving training config:

- resolution: `1024,1024`
- network_dim: `8`
- network_alpha: `1`
- train_batch_size: `16`
- text_encoder_lr: `5e-05`
- unet_lr: `0.0001`
- optimizer: `AdamW`
- epochs: `100`
- xformers enabled

## Known unknowns

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
    "J-YOON/lora-monet-sd1.5",
    weight_name="pytorch_lora_weights.safetensors",
)

prompt = "msl monet, a rainy bridge at sunset, diary illustration, soft brush strokes"
image = pipe(prompt, num_inference_steps=30, guidance_scale=7.0).images[0]
image.save("monet_example.png")
```

## Limitations

- This repository shares the adapter for inference.
- It does not contain the full original training framework.
- Exact end-to-end reproduction of the original run is **Not sure**.

## Gallery

<Gallery>
![Example 1](./images/example_01.png)
![Example 2](./images/example_02.png)
</Gallery>
