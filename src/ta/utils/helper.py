import subprocess, sys,os, sys, subprocess,time,webbrowser,threading,time




def setup_env(venv_dir="venv", requirements_file="requirements.txt"):
    """
    Ensure a local virtual environment exists, install requirements,
    and relaunch inside venv if not already there.
    """
    
    # Path to python inside venv
    python_path = os.path.join(
        venv_dir, "Scripts", "python.exe"
    ) if os.name == "nt" else os.path.join(venv_dir, "bin", "python")

    # Create venv if missing
    if not os.path.exists(venv_dir):
        print(f"📦 Creating virtual environment at {venv_dir}...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    # Relaunch inside venv only once
    if os.environ.get("INSIDE_VENV") != "1":
        print("🔄 Relaunching inside virtual environment...")
        os.environ["INSIDE_VENV"] = "1"
        os.execv(python_path, [python_path] + sys.argv)

    # --- At this point, we are inside venv ---
    print("📦 Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    if os.path.exists(requirements_file):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    print("✅ Virtual environment ready.")





def kill_uvicorn_on_port(port=8000, timeout=5):
    """
    Kill any process using the given port (Windows).
    Wait until the port is free or timeout.
    """
    import time, subprocess

    try:
        result = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True, text=True)
        for line in result.splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[3].endswith(f":{port}") and "LISTENING" in parts:
                pid = parts[-1]
                if pid != "0":
                    print(f"🛑 Killing process on port {port} (PID {pid})")
                    subprocess.run(f'taskkill /PID {pid} /F', shell=True)
    except subprocess.CalledProcessError:
        print(f"✅ No process found on port {port}")

    # 🔄 Wait until port is free
    start = time.time()
    while time.time() - start < timeout:
        try:
            subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True, text=True)
            time.sleep(0.5)
        except subprocess.CalledProcessError:
            print(f"✅ Port {port} is now free")
            return
    print(f"⚠️ Port {port} still busy after {timeout}s")




def open_swagger(url: str = "http://127.0.0.1:8000/docs", delay: float = 1.0):
    """
    Open Swagger docs in the default browser after a small delay.
    Run this before starting uvicorn.run(), since uvicorn is blocking.
    """
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


import subprocess, sys, os, time, webbrowser, threading, shutil

def ensure_cloudflared_binary():
    # Import requests only when needed (after setup_env installs it)
    import requests, platform, stat

    bin_dir = os.path.join(os.getcwd(), "bin")
    os.makedirs(bin_dir, exist_ok=True)

    exe_name = "cloudflared.exe" if os.name == "nt" else "cloudflared"
    bin_path = os.path.join(bin_dir, exe_name)

    if os.path.exists(bin_path):
        return bin_path

    system = platform.system().lower()
    if system == "windows":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    elif system == "linux":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    elif system == "darwin":  # macOS
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
    else:
        sys.exit(f"❌ Unsupported OS: {system}")

    print(f"⬇️ Downloading cloudflared binary from {url} ...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(bin_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    os.chmod(bin_path, os.stat(bin_path).st_mode | stat.S_IEXEC)
    print(f"✅ cloudflared saved to {bin_path}")
    return bin_path



def start_cloudflared():
    """Start cloudflared tunnel after a short delay to let uvicorn boot."""
    time.sleep(3)  # wait for server startup
    cloudflared_bin = ensure_cloudflared_binary()
    if os.name == "nt":
        os.system(f"start cmd /k {cloudflared_bin} tunnel --url http://localhost:8000")
    else:
        os.system(f"{cloudflared_bin} tunnel --url http://localhost:8000 &")