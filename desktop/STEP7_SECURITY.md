# Step 7 — Security, Permissions & Autonomy

Jelon now has a persisted desktop security policy with safe defaults.

Modes:
- ask: no file/process/Git write/push permissions.
- trusted_workspace: explicitly trusted local workspaces can be enabled.
- authorized_repo: required for Git push.

Browser access requires network access. Both are disabled by default.

Settings are stored locally in data/jelon_policy.json.

No Firebase, OpenAI API, or other cloud service is required.

The authorization layer is deliberately separate from the model. The model cannot grant itself permissions.
