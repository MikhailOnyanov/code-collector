# Collect Code

A script to collect source code from multiple directories into a single text file. Perfect for code analysis, sharing projects with AI chatbots, archiving, or creating context for refactoring!

## Features ✨

- Collects `.py` files by default (option to include **all files** 🌐)
- Ignores common directories: `.idea`, `.venv`, `venv`, `__pycache__`, `.env` 🚫
- Add custom directories to exclude 🛑
- Supports multiple input folders 🗂️
- Preserves file structure with relative paths 🧭
- Resilient to file read errors — continues even if some files fail 🔒
- User-friendly CLI with full argument support 🖥️

## Installation 🛠️

1. Make sure you have **Python 3.7+** installed 🐍
2. Clone this repo or copy `collect_code.py` and `setup.py`
3. Install locally with pip:

```bash
pip install -e .
```

After installation, use the `collect-code` command from anywhere! 🚀

### Optional: Install with pipx (recommended for CLI tools) 🧰

```bash
pipx install . --force
```

> 💡 `pipx` ensures isolated, system-wide access to the CLI tool without polluting your global Python environment.

## Usage 🚀

### Collect all `.py` files from one folder:

```bash
collect-code ./src
```

### Collect from multiple folders:

```bash
collect-code ./src ./tests ./utils
```

### Collect **all files** (not just `.py`):

```bash
collect-code ./project --all-files
```

### Exclude additional directories:

```bash
collect-code ./src --exclude node_modules build dist
```

### Example Output 📄

The generated `collected_code.txt` will look like:

```
[project/src/main.py]
def hello():
    print("Hello, world!")

[project/src/utils/helper.py]
class Helper:
    def __init__(self):
        pass

...
```

## Output File 📂

Results are saved to `collected_code.txt` in your current working directory.

## Technical Details ⚙️

- **Language**: Python 3.7+
- **Dependencies**: Standard library only 🚫📦
- **License**: MIT 📜
- **Files**: `collect_code.py`, `setup.py`

## Development 🛠️

Run directly without installation:

```bash
python collect_code.py ./src --all-files
```

## Author 👨‍💻
@MikhailOnyanov

Created to simplify code sharing with AI chat interfaces and streamline project analysis. 💬 🧠

✨ *Because sometimes, the best way to explain code is to send it all at once.*
