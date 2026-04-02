# Architecture Note

## Recommended V1

Use a **text-first pipeline** for the first deployable version.

`diary text -> optional rewrite -> prompt builder -> style LoRA -> composed diary page`

This keeps the system stable and easier to debug.

## Optional multimodal extensions

### V1.5

Add a **reference image** only as a prompt hint or caption source.

### V2

Add true image conditioning:

- **IP-Adapter** when you want image prompting without retraining the base model.
- **ControlNet** when you want spatial control from sketch, edge map, pose, or depth.

## Why not start with full multimodality

Because your current strongest preserved assets are:

- two LoRA adapters on SD1.5
- old diary-generation app logic
- partial training configs and logs

Starting from a narrower V1 lets you finish a clean public demo first.
