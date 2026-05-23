# Environment Setup

Use the currently installed media-generation toolchain first. In the current workflow, `mmx-cli` is the preferred MiniMax path.

## 1. Confirm tool availability

```bash
mmx auth status
```

If `mmx` is unavailable or unauthenticated, fix that before planning any media
generation step.

## 2. Use non-interactive commands in agent workflows

Prefer commands that are deterministic and easy to automate:

```bash
mmx image generate --prompt "minimal product hero background" --out-dir ./tmp --non-interactive --quiet
mmx speech synthesize --text "hello world" --out ./tmp/test.mp3 --non-interactive --quiet
```

Save outputs locally and reference those local files from the frontend.

## 3. Validate the path before scaling up

Run a tiny generation first to confirm:

- auth is working
- output files are written locally
- format and quality are usable for the intended UI

## 4. Legacy compatibility only when required

If the repo or user explicitly requires the old Python scripts:

- verify the script still runs in the current environment
- confirm auth/env assumptions before relying on it
- treat script failure as expected drift, not as the default path

## Next steps

- **Prompt structure**: See [asset-prompt-guide.md](asset-prompt-guide.md)
- **Troubleshooting**: See [troubleshooting.md](troubleshooting.md)
- **Legacy MiniMax details**: See the `minimax-*` guides only when maintaining
  an existing script-based workflow
