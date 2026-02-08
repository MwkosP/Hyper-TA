import typer
from rich.console import Console
from rich.table import Table
import sys
import os
import platform
import subprocess
import webbrowser
import importlib
import pkgutil
import inspect
import ccxt
import time
from typer_ui import TyperUI

import src.ta as ta   # Import your package


# Add the 'src' directory to the path so we can find 'ta'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))


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
#?==============================================================
#?==============================================================
#?==============================================================
#?==============================================================




@app.command()
def github():
    """
    Open the official Hyper-TA Github Website in your browser.
    """
    url = "https://github.com/MwkosP/Hyper-TA/blob/main/README.md"
    console.print(f"📖 [bold]Opening documentation:[/bold] {url}")
    webbrowser.open(url)
#?==============================================================
#?==============================================================
@app.command()
def docs():
    """
    Open technical documentation for the 'ta' Library.
    """
    import webbrowser
    import threading
    import time

    # Use a fixed port or your preferred logic
    port = 8080
    url = f"http://localhost:{port}/ta.html"

    # Define a small function to open the browser after a short delay
    # This gives the server time to start up.
    def open_browser():
        time.sleep(1.5)  # Wait for server to initialize
        webbrowser.open(url)

    console.print(f"🛠️  [bold green]Generating API Documentation...[/bold green]")
    console.print(f"📖 [cyan]Opening browser at {url}[/cyan]")

    # Start the browser-opener in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run pdoc server
    try:
        # Set PYTHONPATH so pdoc finds your 'src' folder
        env = os.environ.copy()
        env["PYTHONPATH"] = f"src{os.pathsep}{env.get('PYTHONPATH', '')}"
        
        # Execute pdoc without the --browse flag
        subprocess.run([
            sys.executable, "-m", "pdoc", 
            "ta", 
            "--port", str(port)
        ], env=env)
    except KeyboardInterrupt:
        console.print("\n🛑 Documentation server closed.")


#?==============================================================
#?==============================================================

@app.command(name="guide")
def guide():
    """
    Display a quick-start guide for Threshold and Mixed strategies.
    """
    console.print("📘 [bold]Hyper-TA Strategy Guide[/bold]", style="underline")
    console.print("\n[bold cyan]1. Thresholds:[/bold cyan]")
    console.print("   Defined by upper/lower bounds. Triggers when price/indicator crosses these levels.")
    
    console.print("\n[bold magenta]2. Mixed Thresholds:[/bold magenta]")
    console.print("   Combines multiple signals (e.g., RSI + Volume) for higher probability trades.")
    
    console.print("\n[bold yellow]3. Best Practices:[/bold yellow]")
    console.print("   Always run [green]ta health[/green] before starting a new backtest session")

#?==============================================================
#?==============================================================




@app.command()
def test(
    coverage: bool = typer.Option(False, "--cov", help="Run tests with coverage report"),
    file: str = typer.Option(None, "--file", "-f", help="Run a specific test file")
):
    """
    Run the project test suite using pytest.
    """
    console.print("🧪 [bold]Initializing Test Suite...[/bold]")
    
    # Base command
    cmd = ["uv", "run", "python", "-m", "pytest"]
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=ta", "--cov-report=term-missing"])
        
    # Target specific file or the whole directory
    if file:
        cmd.append(f"tests/{file}")
    else:
        cmd.append("tests/")

    try:
        # Execute the command
        subprocess.run(cmd, check=True)
        console.print("\n✅ [bold green]All tests passed![/bold green]")
    except subprocess.CalledProcessError:
        console.print("\n❌ [bold red]Tests failed. Check the output above for errors.[/bold red]")
        sys.exit(1)

#?==============================================================
#?==============================================================



# --- Health Command ---
@app.command()
def health():
    """Check the system health and project environment."""
    table = Table(title="🏥 System Health Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="white")

    # Check Python Version
    table.add_row("Python", "✅", f"{platform.python_version()}")
    
    # Check if .env exists
    env_exists = os.path.exists(".env")
    table.add_row("Env File", "✅" if env_exists else "❌", ".env found" if env_exists else "Missing .env")
    
    # Check for Data folder
    data_dir = "src/ta/data"
    data_exists = os.path.exists(data_dir)
    table.add_row("Data Dir", "✅" if data_exists else "⚠️", "Ready" if data_exists else "Dir missing")

    console.print(table)


#?==============================================================
#?==============================================================
@app.command()
def version():
    """Display the current version of Hyper-TA."""
    console.print("🚀 [bold]Hyper-TA[/bold] Version: [cyan]0.1.0[/cyan]")


#?==============================================================
#?==============================================================


@app.command()
def fetch(
    ticker: str = typer.Argument("BTC/USDT", help="The symbol to fetch (e.g., ETH/USDT)"),
    exchange_id: str = typer.Option("binance", "--ex", help="Exchange to use")
):
    """
    Fetch the current live price for a specific ticker.
    """
    console.print(f"🔍 [bold]Fetching {ticker} from {exchange_id}...[/bold]")
    
    try:
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_id)()
        
        # Fetch the ticker data
        data = exchange_class.fetch_ticker(ticker)
        
        # Display the result in a clean panel
        last_price = data['last']
        change = data['percentage']
        color = "green" if change >= 0 else "red"

        table = Table(show_header=False, border_style="cyan")
        table.add_row("Symbol", ticker)
        table.add_row("Live Price", f"[bold yellow]${last_price:,.2f}[/bold yellow]")
        table.add_row("24h Change", f"[{color}]{change:.2f}%[/{color}]")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error:[/red] Could not fetch {ticker}. Ensure the symbol format is correct (e.g., BTC/USDT).")


#?==============================================================
#?==============================================================
'''
@app.command()
def logs(
    lines: int = typer.Option(10, "--lines", "-n", help="Number of last lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output in real-time")
):
    """
    View and monitor project logs.
    """
    log_file = "src.ta.log" # Or wherever your logger saves files

    if not os.path.exists(log_file):
        console.print(f"[bold red]Error:[/bold red] Log file '{log_file}' not found.")
        return

    def print_logs(count):
        with open(log_file, "r") as f:
            # Get the last N lines
            content = f.readlines()
            last_lines = content[-count:]
            for line in last_lines:
                # Basic color coding for log levels
                if "ERROR" in line:
                    console.print(f"[red]{line.strip()}[/red]")
                elif "INFO" in line:
                    console.print(f"[cyan]{line.strip()}[/cyan]")
                else:
                    console.print(line.strip())

    console.print(f"📄 [bold]Showing last {lines} lines of {log_file}:[/bold]\n")
    print_logs(lines)

    if follow:
        console.print("\n👀 [yellow]Watching for new entries... (Ctrl+C to stop)[/yellow]")
        try:
            with open(log_file, "r") as f:
                f.seek(0, 2)  # Go to end of file
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    console.print(line.strip())
        except KeyboardInterrupt:
            console.print("\nStopped watching logs.")
'''


#?==============================================================
#?==============================================================



@app.command(name="list-functions")
def list_functions(
    module_name: str = typer.Option("ta", "--module", "-m", help="Sub-module to scan")
):
    """
    List all functions within the ta package.
    """
    table = Table(title=f"🔍 Functions in '{module_name}'")
    table.add_column("Module", style="cyan")
    table.add_column("Function Name", style="green")

    try:
        # Import the base package
        package = importlib.import_module(module_name)
        
        # Walk through all sub-modules
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            try:
                mod = importlib.import_module(name)
                # Find functions defined in this module (skip imports)
                for func_name, obj in inspect.getmembers(mod, inspect.isfunction):
                    if obj.__module__ == name:
                        table.add_row(name.split('.')[-1], func_name)
            except Exception:
                continue # Skip modules that fail to load
                
        console.print(table)
    except ModuleNotFoundError:
        console.print(f"[red]Error:[/red] Could not find module '{module_name}'. Check your src folder.")




#?==============================================================
#?==============================================================    
THRESHOLD_REGISTRY = {
    "crossUpThreshold": { "desc": "Triggers when crosses specified price."},
    "crossUpLineThreshold": { "desc": "Triggers when crosses specified Line."},
    "inRangeThreshold": { "desc": "Triggers when enters specified range."},
    "timeThreshold": { "desc": "Triggers when stays >= than specified time."},
    "mixThresholds": { "desc": "Combines Multiple Thresholds Logic/Signals into new Signals."},
}    

@app.command(name="list-thresholds")
def list_thresholds():
    """
    List all available Threshold and Mixed Threshold strategies.
    """
    table = Table(title="📈 Threshold Catalog")
    table.add_column("Threshold Name", style="cyan")
    table.add_column("What it does", style="white")

    for name, info in THRESHOLD_REGISTRY.items():
        table.add_row(name, info["desc"])

    console.print(table)
#?==============================================================
#?==============================================================
@app.command(name="list-strategies")
def list_strategies():
    """
    List all specific Threshold and Mixed Threshold strategy types.
    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Threshold Name", style="cyan", width=22)
    table.add_column("What it does", style="white")

    # Your specific Threshold logic
    strategies = [
        ("mixThresholds", "Combines Multiple Thresholds Logic/Signals into new Signals."),

    ]
    
    # Adding a separator for Mixed Thresholds
    for name, desc in strategies:
        table.add_row(name, desc)

    # Automatically scan for your Mixed Threshold files too
    strat_path = "src/ta/strategies"
    if os.path.exists(strat_path):
        files = [f.replace(".py", "") for f in os.listdir(strat_path) 
                 if "mix" in f.lower() and f.endswith(".py")]
        
        if files:
            table.add_section() # Adds that horizontal line between groups
            for mix_name in files:
                table.add_row(mix_name, "Mixed: Combines multiple threshold triggers.")

    console.print(table)



if __name__ == "__main__":
    app()