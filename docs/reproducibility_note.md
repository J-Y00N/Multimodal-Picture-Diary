# Reproducibility Note

Exact reproduction of the original LoRA training runs is **Not sure**.

What is preserved:

- `monet_last_20231129-043745.json`
- `painting_v1_20231211-043052.json`
- `painting_script_caption.txt`
- `animation_training_log.txt`

What is not fully preserved:

- seed values (blank in the preserved JSON files)
- exact dataset snapshot
- exact folder contents at train time
- exact mapping between the local `painting_v1` artifact name and the public `animate-lora-sd1.5` checkpoint

What this repository claims:

- preserved training provenance
- deployable inference app
- transparent documentation of known unknowns

What this repository does **not** claim:

- exact end-to-end reproduction of the original training runs
- full vendored training framework
