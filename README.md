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

### Current status

The agent controller now sends the local model a structured tool catalog, parses strict JSON plans, executes only registered permission-approved tools, and feeds failures into bounded correction. The local model adapter supports a real llama.cpp GGUF backend when the optional dependency and a compatible model file are installed.

Network, browser, process execution, Git writes, and Git pushes are disabled unless explicitly granted by policy.

## Development

Run the core tests with:

```bash
python -m unittest discover -s tests -v
```

Target release platform: Windows 10/11 64-bit.
