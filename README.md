# Jelon

Offline-first autonomous desktop AI agent.

## v0.1 core

- Local model adapter boundary (no cloud API key required)
- Bounded goal -> plan -> tool -> observe -> correct loop
- Permission-aware tool registry
- Persistent local task/skill learning
- Bounded self-correction
- Browser/research and computer-tool boundaries
- Windows desktop host + Python agent engine
- Windows desktop UI + JSONL Python bridge

### Current status

The agent controller sends the local model a structured tool catalog, parses strict JSON plans, executes only registered permission-approved tools, and feeds failures into bounded correction. The local model adapter supports a real llama.cpp GGUF backend when the optional dependency and a compatible model file are installed.

Step 6 now includes a WPF desktop shell under `desktop/Jelon.Desktop`. During development it starts `python -m engine.desktop_server` and communicates through JSON Lines over stdin/stdout. If `JELON_MODEL_PATH` is not configured, the UI remains usable for status/bridge testing but will not pretend that an AI model is running.

Network, browser, process execution, Git writes, and Git pushes are disabled unless explicitly granted by policy.

## Desktop development

Requirements:

- Windows 10/11 64-bit
- .NET 8 SDK
- Python available on PATH
- Repository checkout

From the repository root:

```bash
dotnet run --project desktop/Jelon.Desktop/Jelon.Desktop.csproj
```

Optional local model path:

```powershell
$env:JELON_MODEL_PATH="C:\models\jelon.gguf"
dotnet run --project desktop/Jelon.Desktop/Jelon.Desktop.csproj
```

The development bridge is intentionally separate from the eventual installer. Step 8 will package the Python runtime, local model/runtime, dependencies, and desktop executable into a standalone installer.

## Core tests

```bash
python -m unittest discover -s tests -v
```

Target release platform: Windows 10/11 64-bit.
