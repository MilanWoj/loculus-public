# Loculus

100% local AI search engine for macOS (Apple Silicon). It combines web search (SearXNG) and RAG over your personal documents (Qdrant), synthesized by a local LLM (llama.cpp) with cited sources, and nothing ever leaves your machine.

Target RAM footprint: < 8-10 GB. Everything (LLM, Docker containers, servers) stops automatically as soon as you close the application window.

## Requirements

- macOS on Apple Silicon
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running)
- Git

```bash
brew install cmake openssl@3
```

## Installation

```bash
git clone --recurse-submodules https://github.com/MilanWoj/loculus-public.git loculus
cd loculus

# Build llama.cpp (Metal acceleration)
cd infra/llama.cpp
cmake -B build -DGGML_METAL=ON -DLLAMA_OPENSSL=ON -DOPENSSL_ROOT_DIR=$(brew --prefix openssl@3)
cmake --build build --config Release -j
sudo ln -sf "$(pwd)/build/bin/llama-server" /opt/homebrew/bin/llama-server
cd ../..

# Configure SearXNG
cp infra/docker/searxng/settings.yml.example infra/docker/searxng/settings.yml
# Then replace secret_key with a value generated with: openssl rand -hex 32
```

The backend and the frontend require no installation on your machine: Docker builds them on first launch.

## Usage

```bash
./scripts/start-prod.sh   # start the whole stack
./scripts/status.sh       # check the state of the services
./scripts/stop.sh         # stop everything
```

## macOS app

To package Loculus as a `.app` (starts and stops automatically when the window is opened or closed):

```bash
./macos/build_app.sh
open build-macos/Loculus.app
```

Then move `Loculus.app` to `/Applications` if you like.

## Document ingestion

Put your files (PDF, DOCX, TXT, MD) in the `documents/` folder, then, with the stack running:

```bash
docker compose -f infra/docker/docker-compose.yml exec backend python -m app.rag.ingest /app/documents
```

## Scripts

| Script | Purpose |
|---|---|
| `scripts/start.sh` | Starts the stack in development mode |
| `scripts/start-prod.sh` | Starts the stack in production mode (containers) |
| `scripts/stop.sh` | Stops all processes and containers |
| `scripts/status.sh` | Shows the state of the services and RAM usage |
| `scripts/rebuild.sh` | Rebuilds the backend Docker image |
| `macos/build_app.sh` | Builds the native macOS application |

## Architecture

- `backend/`: FastAPI API (RAG orchestration + web search + SSE streaming)
- `frontend/`: React + Vite + Tailwind interface
- `infra/docker/`: Qdrant, SearXNG, backend image
- `macos/`: native Swift/Cocoa/WKWebView application
- `scripts/`: stack lifecycle (start, stop, metrics)

## License

MIT, see [LICENSE](LICENSE).
