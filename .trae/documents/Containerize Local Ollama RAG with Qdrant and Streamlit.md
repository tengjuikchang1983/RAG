## Short Answer

* Do NOT use `127.0.0.1` inside containers to reach host Ollama. Use `http://host.docker.internal:11434` on macOS.

* If you run the app outside Docker (directly on your Mac), then `http://127.0.0.1:11434` is correct.

## Why

* `127.0.0.1` from within a container points to the container itself, not your host.

* Docker Desktop exposes the host to containers via `host.docker.internal` on macOS.

## Compose Setting (Mac)

```yaml
environment:
  OLLAMA_HOST: http://host.docker.internal:11434
```

## Connectivity Test

* Host: `curl http://localhost:11434/api/tags`

* Container: `docker run --rm curlimages/curl http://host.docker.internal:11434/api/tags`

## Proceed

* Keep the rest of the plan unchanged (Qwen3:4b + Qdrant + Streamlit).

