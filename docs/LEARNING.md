# Jelon learning layer

Jelon separates **model knowledge** from **agent learning**.

- The local model supplies language/reasoning.
- LearningStore records task outcomes and reusable procedures.
- Skills can be marked verified only after a procedure has a source and a successful test.
- SelfCorrection provides bounded retry instructions after failed tool observations.
- Network/browser permissions remain disabled by default.

This layer does not silently retrain model weights. It builds a persistent local knowledge base that can be retrieved by future tasks.
