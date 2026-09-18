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

The agent controller, permission layer, learning store, and self-correction layer are implemented as local foundations. The local model adapter is still an inference boundary: a real local model runtime must be connected before Jelon can perform open-ended reasoning.

Network, browser, process execution, Git writes, and Git pushes are disabled unless explicitly granted by policy.

## Development

Run the core tests with:

```bash
python -m unittest discover -s tests -v
```

Target release platform: Windows 10/11 64-bit.
