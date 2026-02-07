# HyperTA - Setup Instructions

## Quick Start
```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone https://github.com/MwkosP/Hyper-TA.git
cd Hyper-TA
uv sync

# 3. Run
uv run python main.py
```

That's it!

## Development
```bash
# Add a package
uv add package-name

# Run tests
uv run pytest

# Update dependencies
uv sync --upgrade
```

## Troubleshooting

**`uv` not found?**
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

**Need to use pip instead?**
```bash
pip install -e .
```