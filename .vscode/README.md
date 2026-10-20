# Running the web app from VS Code

This repo ships a VS Code task, **Run Server**, that starts the Flask app in `./server` using a conda environment you choose each time it runs.

## Prerequisites

- VS Code, with the repo opened as the workspace folder (`SqlDatabase`).
- Conda (Miniconda or Anaconda) installed and available as `conda` on your `PATH`. If it is not on the `PATH`, the script falls back to `~/miniconda3/bin/conda`.
- A bash shell: Linux, macOS, WSL, or Git Bash on Windows.
- A conda environment with the server dependencies installed (see below).
- A `.env` file in the repo root with the database credentials. Copy `env_example.txt` to `.env` and fill it in.

## One-time setup: create an environment

```bash
conda create -n sql python=3.13
conda activate sql
pip install -r server/requirements.txt
```

Any environment name works. The task lists every environment conda knows about.

## Start the server

1. Open the repo in VS Code.
2. Press `Ctrl+Shift+B` (macOS: `Cmd+Shift+B`). Alternatively, open the Command Palette (`Ctrl+Shift+P`), choose **Tasks: Run Build Task**, or choose **Tasks: Run Task** and then **Run Server**.
3. A terminal panel opens and shows a numbered list:

   ```
   Select conda environment:
   1) base          3) phd     5) sql
   2) defect-atlas  4) prep
   #?
   ```

4. Type the number of the environment you want and press `Enter`.
5. Flask starts. Open <http://localhost:5000> in your browser.

The app runs in debug mode, so it reloads when you edit `server/app.py`.

## Stop the server

Click into the task terminal and press `Ctrl+C`, or click the trash icon on the terminal.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | The chosen environment lacks the dependencies. Pick another one, or run `pip install -r server/requirements.txt` in it. |
| `Permission denied` or `bad interpreter` | The task must launch the script through `bash`, as `tasks.json` does. Do not run `run_server.sh` directly on filesystems mounted `noexec`. |
| `conda: command not found` | Install conda or add it to your `PATH`. Then restart VS Code. |
| The menu does not appear | Check that the task command in `.vscode/tasks.json` is `bash "${workspaceFolder}/.vscode/run_server.sh"`. |
| Database connection errors | Check `.env` in the repo root (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`) and that you can reach the database host. |
| Port 5000 already in use | Stop the other process using it, or change the port in the last line of `server/app.py`. |

## How it works

- `.vscode/tasks.json` defines the **Run Server** task and sets it as the default build task.
- `.vscode/run_server.sh` reads `conda env list`, shows the menu with bash `select`, then runs `conda run --no-capture-output -n <env> python app.py` from `./server`.

To add a new environment to the menu, create it with conda. No file edits are needed.
