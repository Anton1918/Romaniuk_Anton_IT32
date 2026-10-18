# Dev container

Open the repo in VS Code and run **Dev Containers: Reopen in Container**. The container has Python 3.12, `uv`, the MkDocs toolchain in `.venv` and Claude Code.

```bash
uv run mkdocs serve -a 0.0.0.0:8000
```

Claude Code inside the container keeps its login in a separate Docker volume (`CLAUDE_CONFIG_DIR=/home/vscode/.claude`), not in your host `~/.claude`. Run `claude` in the container terminal and sign in with the account you want to use there; your host login is not affected. The login survives container rebuilds. To sign out completely, delete the `claude-code-config-*` volume.

GitHub CLI (`gh`) is installed too. Run `gh auth login` once in the container terminal; the login is kept in the `gh-config-*` volume and survives rebuilds.

# Run locally

```bash
python3 -m venv env
source  env/bin/activate
pip3 install -r requirements.txt
mkdocs serve --livereload
```
