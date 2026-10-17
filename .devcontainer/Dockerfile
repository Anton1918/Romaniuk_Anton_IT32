FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# uv: Python package manager used for the docs toolchain
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /usr/local/bin/

# Claude Code (native installer), installed for the non-root user
USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash
ENV PATH="/home/vscode/.local/bin:${PATH}"
