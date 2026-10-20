#!/usr/bin/env bash
# Prompt for a conda environment, then start the web app in ./server with it.
set -e
CONDA_BIN="${CONDA_EXE:-$(command -v conda || echo "$HOME/miniconda3/bin/conda")}"
mapfile -t ENVS < <("$CONDA_BIN" env list | awk '!/^#/ && NF {print $1}')
echo "Select conda environment:"
select ENV in "${ENVS[@]}"; do
    [ -n "$ENV" ] && break
    echo "Invalid choice."
done
cd "$(dirname "$0")/../server"
exec "$CONDA_BIN" run --no-capture-output -n "$ENV" python app.py
