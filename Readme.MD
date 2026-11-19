# Toonity

**Text- and image-to-3D model generation for game developers.**

Toonity turns a short text prompt or a reference image into a game-ready 3D mesh. It wraps pretrained generative 3D models behind a small local API, then simplifies and smooths the output so it can be used directly in a game engine such as Unity.

This repository contains the research prototype developed in the TÜBİTAK 1507 SME R&D project *Toonity* (project no. 7240695, October 2024 – February 2026) at Bermuda Games.

---

## How it works

```
 Client (web app / Unity plugin / curl)
        │  POST /generate  {"text": "..."}  or  {"image": "<base64>"}
        ▼
 ┌──────────────────────┐        ┌─────────────────────────────┐
 │  Mainframe (FastAPI) │ ─────► │  Inter-system (FastAPI)     │
 │  mainframe/          │ ◄───── │  inter-systems/hunyuan/     │
 │  port 1380           │  uid   │  or inter-systems/shap-e/   │
 └──────────┬───────────┘        │  port 1381                  │
            │                    └──────────────┬──────────────┘
            │  GET /status/{uid}                │ runs the model in a
            │                                   │ background thread and
            ▼                                   ▼ writes exports/{uid}.obj
 ┌──────────────────────────────────────────────────────────────┐
 │  Post-processing (mainframe)                                 │
 │  1. Fast Quadric Mesh Simplification  → fewer triangles      │
 │  2. Laplacian smoothing               → smoother surface     │
 └──────────────────────────────────────────────────────────────┘
```

1. **Mainframe** (`mainframe/mainframe_api.py`) is the single entry point. It forwards requests to the active model service and post-processes the finished mesh.
2. **Inter-systems** (`inter-systems/`) are thin API wrappers, one per model. Each one runs in its own environment, so models with conflicting dependencies do not affect each other. All of them share the same interface (`ModuleBaseClass.py`) and the same two endpoints.
3. **Generation is asynchronous.** `POST /generate` returns a unique id immediately; the client polls `GET /status/{uid}` until the mesh is ready.
4. **Post-processing** reduces the triangle count with Fast Quadric Mesh Simplification and then applies Laplacian smoothing, producing a low-poly mesh suitable for games.

### Supported models

| Model | Input | Pipeline | Wrapper |
|---|---|---|---|
| [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) (Tencent) | text or image | text → image (HunyuanDiT) → background removal → mesh → texture | `inter-systems/hunyuan/` |
| [Shap-E](https://github.com/openai/shap-e) (OpenAI) | text | text → mesh | `inter-systems/shap-e/` |

During the project several other open models were benchmarked (Stable-DreamFusion, DreamGaussian, Zero-1-to-3, Fantasia3D, Magic3D, SJC) on output quality, inference time, GPU memory and triangle count. Hunyuan3D-2 and Shap-E were selected for the prototype; image-to-3D with Hunyuan3D-2 gave the most controllable and fastest results, especially for characters.

---

## Repository structure

```
toonity/
├── mainframe/
│   ├── mainframe_api.py        # entry point API (port 1380), forwards requests and post-processes meshes
│   ├── laplace_smoothing.py    # Laplacian mesh smoothing (NumPy)
│   └── simplify.exe            # Fast Quadric Mesh Simplification binary (third-party, see below)
├── inter-systems/
│   ├── ModuleBaseClass.py      # common base class for all model wrappers
│   ├── hunyuan/
│   │   ├── hunyuan.py          # Hunyuan3D-2 text/image-to-3D module
│   │   └── hunyuan_api.py      # FastAPI wrapper (port 1381)
│   └── shap-e/
│       ├── shapE.py            # Shap-E text-to-3D module
│       └── shapE_api.py        # FastAPI wrapper (port 1381)
├── FastQuadricMeshSimplifier/  # Unity Editor tool for interactive mesh simplification
│   ├── MeshSimplifierEditor.cs # editor window: Window > Hyper > Mesh Simplifier
│   ├── MeshUtility.cs          # mesh extraction and export helpers
│   └── Core/                   # C# mesh simplification library (third-party based, see below)
└── modules/                    # git submodules: original model repositories
```

---

## Getting started

### Requirements

- Python 3.10
- An NVIDIA GPU with CUDA (tested on an RTX 4070 Ti)
- [Conda](https://docs.conda.io/) or another tool for separate environments (one per model is recommended)

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/viol3/toonity.git
```

If you already cloned the repository:

```bash
git submodule update --init --recursive
```

### 2. Install a model

Follow the installation instructions of the model you want to use inside `modules/`, for example `modules/Hunyuan3D-2/README.md`. Then install the API dependencies in the same environment:

```bash
pip install fastapi uvicorn requests numpy pillow
```

> **Note:** `hunyuan.py` and `shapE.py` add the model folders to `sys.path` with absolute Windows paths (`C:/Users/...`). Change these lines to match your own clone before running.

### 3. Start the services

Start one model service (both use port 1381, so run one at a time):

```bash
cd inter-systems/hunyuan
python hunyuan_api.py
```

In a second terminal, start the mainframe:

```bash
cd mainframe
python mainframe_api.py
```

### 4. Generate a model

Text to 3D:

```bash
curl -X POST http://127.0.0.1:1380/generate -d "{\"text\": \"a wooden treasure chest\"}"
```

Image to 3D: send the image as a base64 string in the `image` field instead of `text`. An optional `seed` can be passed as well.

The response contains a `uid`. Poll the status until it is `completed`:

```bash
curl http://127.0.0.1:1380/status/<uid>
```

When generation finishes, the mainframe simplifies the mesh and writes a smoothed copy (`<uid>.obj_smoothed.obj`) to its working directory.

---

## Post-processing

**Fast Quadric Mesh Simplification.** Generated meshes often have hundreds of thousands of triangles. The mainframe calls the `simplify` binary with a target ratio of `0.01`, keeping about 1% of the triangles while preserving the overall shape.

**Laplacian smoothing** (`mainframe/laplace_smoothing.py`). Simplification can leave a rough surface. Each vertex is moved towards the average of its neighbours:

```
v_i ← v_i + λ · (mean(neighbours(v_i)) − v_i)
```

The prototype uses λ = 0.25 and 4 iterations. The script builds the vertex adjacency directly from the faces of the `.obj` file and needs only NumPy:

```bash
python laplace_smoothing.py model.obj
```

**Unity Editor tool** (`FastQuadricMeshSimplifier/`). The same simplification is available inside Unity through `Window > Hyper > Mesh Simplifier`. The window shows a live preview of the mesh and lets you set the simplification quality and aggressiveness, choose which edges to preserve (border, UV seam, UV foldover, surface curvature) and export the result as a mesh asset.

---

## Status and limitations

- This is a research prototype that runs on `localhost`. It is not hardened for production use (open CORS, no authentication).
- Only one model service can run at a time on the default port.
- Model weights are downloaded at runtime and are not part of this repository.
- Evaluation reports and generated outputs are kept locally and are excluded through `.gitignore`.

---

## Third-party code and licenses

This repository builds on the following open-source work. Each component keeps its own license:

| Component | Used in | Source | License |
|---|---|---|---|
| Hunyuan3D-2 | `modules/Hunyuan3D-2` (submodule) | [Tencent-Hunyuan/Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) | See the original repository |
| Shap-E | `modules/shap-e` (submodule) | [openai/shap-e](https://github.com/openai/shap-e) | MIT |
| DreamGaussian, Fantasia3D, ProlificDreamer | `modules/` (submodules, benchmarking only) | see `.gitmodules` | See the original repositories |
| Fast Quadric Mesh Simplification (`simplify` binary) | `mainframe/simplify.exe` | [sp4cerat/Fast-Quadric-Mesh-Simplification](https://github.com/sp4cerat/Fast-Quadric-Mesh-Simplification) | MIT |
| UnityMeshSimplifier | `FastQuadricMeshSimplifier/Core/` (adapted, namespace renamed) | [Whinarn/UnityMeshSimplifier](https://github.com/Whinarn/UnityMeshSimplifier) | MIT |

---

## Acknowledgements

Developed by [Bermuda Games](https://bermuda.gs) with support from the TÜBİTAK 1507 SME R&D Start-up Support Programme (project no. 7240695).
