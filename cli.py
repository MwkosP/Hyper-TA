import typer
from rich.console import Console
from rich.table import Table

# Initialize the Typer app
app = typer.Typer(help="Hyper-TA Strategy Management CLI")
console = Console()

# This part is NEW: It tells Typer to treat this as a group
@app.callback()
def callback():
    """
    Hyper-TA Command Line Interface
    """
    pass

STRATEGY_REGISTRY = {
    "threshold_standard": {"type": "Standard", "desc": "Basic upper/lower bound triggers."},
    "mix_threshold_v1": {"type": "Mixed", "desc": "Combines Volume spikes with RSI."}
}

@app.command(name="list")
def list_strategies():
    """
    List all available Threshold and Mixed Threshold strategies.
    """
    table = Table(title="📈 Strategy Catalog")
    table.add_column("Command Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("What it does", style="white")

    for name, info in STRATEGY_REGISTRY.items():
        table.add_row(name, info["type"], info["desc"])

    console.print(table)

if __name__ == "__main__":
    app()