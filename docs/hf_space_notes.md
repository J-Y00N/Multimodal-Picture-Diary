# Hugging Face Space Notes

Use a **Docker Space** for this Streamlit app.

Important settings:

- `sdk: docker`
- `app_port: 7860`
- `.streamlit/config.toml` with `enableXsrfProtection = false`

Recommended secrets / variables:

- `OPENAI_API_KEY` (secret, optional)
- `HF_TOKEN` (secret, optional)
- `MONET_LORA_REPO_ID` (variable)
- `ANIMATE_LORA_REPO_ID` (variable)

Recommended V1 deployment behavior:

- do not rely on persistent local storage
- allow preview + download instead of permanent gallery saving
- keep image size moderate (512 or 768) for faster inference
