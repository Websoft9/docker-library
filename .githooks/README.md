# Local Git Hooks

This repository provides local hooks to catch AI command adapter drift before push.

Enable them once:

```bash
make install-git-hooks
```

Installed hooks:

- `pre-commit`: runs `make build-ai-commands ARGS="--check"`
- `pre-push`: runs the same check and `tests/build/test_build_ai_commands.py` when `.venv` exists
