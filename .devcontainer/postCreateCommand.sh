#!/bin/bash
set -e

GREEN='\e[0;32m'
YELLOW='\e[0;33m'
NC='\e[0m'

# A fresh Docker volume is owned by root; Claude Code must be able to write its config there
sudo chown -R vscode:vscode "${CLAUDE_CONFIG_DIR}" /home/vscode/.config/gh

printf "${GREEN}Installing MkDocs toolchain into .venv...${NC}\n"
uv venv --allow-existing "${UV_PROJECT_ENVIRONMENT}"
uv pip install --python "${UV_PROJECT_ENVIRONMENT}" -r requirements.txt

# The skill lives in .claude/skills/ (git-ignored, local only), so install its deps only if it is there
if [ -f .claude/skills/lecture-materials/package.json ]; then
    printf "${GREEN}Installing lecture-materials skill dependencies...${NC}\n"
    (cd .claude/skills/lecture-materials && npm install --no-audit --no-fund)
fi

printf "${GREEN}Claude Code: $(claude --version)${NC}\n"
if [ ! -f "${CLAUDE_CONFIG_DIR}/.credentials.json" ]; then
    printf "${YELLOW}Claude Code is not logged in yet. Run 'claude' and sign in with the account for this container.${NC}\n"
fi

if ! gh auth status >/dev/null 2>&1; then
    printf "${YELLOW}GitHub CLI is not logged in yet. Run 'gh auth login' to push and open pull requests.${NC}\n"
fi

printf "${GREEN}Done. Preview the site: uv run mkdocs serve -a 0.0.0.0:8000${NC}\n"
