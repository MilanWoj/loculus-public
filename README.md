# Loculus

Moteur de recherche IA 100% local pour macOS (Apple Silicon). Combine recherche web (SearXNG) et RAG sur vos documents personnels (Qdrant), synthétisés par un LLM local (llama.cpp) avec citations des sources — dans l'esprit de Perplexity, sans jamais quitter votre machine.

Empreinte RAM cible : < 8-10 Go. Tout s'arrête automatiquement (LLM, conteneurs Docker, serveurs) dès que vous fermez la fenêtre de l'application.

## Prérequis

- macOS Apple Silicon
- [Homebrew](https://brew.sh)
- Docker Desktop
- Git
- Xcode Command Line Tools : `xcode-select --install`

## Installation

```bash
git clone https://github.com/MilanWoj/loculus.git
cd loculus

brew install cmake openssl@3 node uv

git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_METAL=ON -DLLAMA_OPENSSL=ON -DOPENSSL_ROOT_DIR=$(brew --prefix openssl@3)
cmake --build build --config Release -j
sudo cp build/bin/llama-server /opt/homebrew/bin/
cd ..

cp infra/docker/searxng/settings.yml.example infra/docker/searxng/settings.yml
# Puis remplacez secret_key par une valeur générée avec : openssl rand -hex 32

cd backend && uv sync && cd ..
cd frontend && npm install && cd ..
```

## Lancement (mode développement)

```bash
./scripts/start.sh
```

Ouvre le frontend sur `http://127.0.0.1:5173` avec hot reload.

## Lancement (mode production, conteneurisé)

```bash
./scripts/start-prod.sh
```

Sert l'application complète sur `http://127.0.0.1:8000`.

## Ingestion de documents

```bash
cd backend
uv run python -m app.rag.ingest /chemin/vers/vos/documents
```

## Arrêt

```bash
./scripts/stop.sh
```

## Application macOS

Pour empaqueter Loculus en `.app` (démarrage/arrêt automatique à l'ouverture/fermeture de la fenêtre) :

```bash
./macos/build_app.sh
open build-macos/Loculus.app
```

Puis, si besoin, déplacez `Loculus.app` dans `/Applications`.

## Scripts

| Script | Rôle |
|---|---|
| `scripts/start.sh` | Démarre la stack en mode développement |
| `scripts/start-prod.sh` | Démarre la stack en mode production (conteneurs) |
| `scripts/stop.sh` | Arrête tous les processus et conteneurs |
| `scripts/status.sh` | Affiche l'état des services et la consommation RAM |
| `scripts/rebuild.sh` | Reconstruit l'image Docker du backend |
| `macos/build_app.sh` | Compile l'application macOS native |

## Architecture

- `backend/` — API FastAPI (orchestration RAG + recherche web + streaming SSE)
- `frontend/` — interface React + Vite + Tailwind
- `infra/docker/` — Qdrant, SearXNG, image du backend
- `macos/` — application native Swift/Cocoa/WKWebView
- `scripts/` — cycle de vie de la stack (démarrage, arrêt, métriques)

## Licence

MIT — voir [LICENSE](LICENSE).
