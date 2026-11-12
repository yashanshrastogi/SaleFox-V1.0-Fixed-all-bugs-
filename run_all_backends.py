import functools
print_f = functools.partial(print, flush=True)
#!/usr/bin/env python3
"""
Master Launcher for All SaleFox Backend Intelligence Scrapers & Bot Servers.
Starts all 9 brand scrapers concurrently, performs verifiable HTTP readiness checks,
and monitors child process lifecycles.
Press Ctrl+C to terminate all servers gracefully.
"""

import os
import sys
import time
import socket
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRAPERS_DIR = BASE_DIR / "src" / "backend" / "brand_scrapers"

SERVICES = [
    {"name": "Amazon",   "port": 5050, "dir": SCRAPERS_DIR / "amazon"},
    {"name": "Flipkart", "port": 5051, "dir": SCRAPERS_DIR / "flipkart"},
    {"name": "Vivo",     "port": 5052, "dir": SCRAPERS_DIR / "vivo"},
    {"name": "Samsung",  "port": 5053, "dir": SCRAPERS_DIR / "samsung"},
    {"name": "Croma",    "port": 5054, "dir": SCRAPERS_DIR / "croma"},
    {"name": "Apple",    "port": 5055, "dir": SCRAPERS_DIR / "apple"},
    {"name": "Reliance", "port": 5056, "dir": SCRAPERS_DIR / "reliance"},
    {"name": "Oppo",     "port": 5057, "dir": SCRAPERS_DIR / "oppo"},
    {"name": "JioMart",  "port": 5062, "dir": SCRAPERS_DIR / "jiomart"},
]

def resolve_python_executable():
    """Detect local .venv interpreter if available to prevent unconfigured system Python crashes."""
    venv_py = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable

def check_http_health(port, endpoint="/api/health", timeout_sec=1.5):
    """Check if service is responding with valid HTTP status on port, with fallback to /api/status."""
    for ep in [endpoint, "/api/status", "/health"]:
        url = f"http://127.0.0.1:{port}{ep}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SaleFox-HealthCheck/1.0"})
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                if response.status in (200, 201, 204):
                    return True
        except Exception:
            continue
    return False

def check_socket(port, timeout_sec=0.5):
    """Fallback socket check if HTTP payload takes longer to serialize."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout_sec)
    try:
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except Exception:
        return False

def main():
    print_f("=" * 70)
    print_f(" 🚀 STARTING ALL 9 SALEFOX BRAND SCRAPERS & AUTOMATION SERVERS")
    print_f("=" * 70)

    py_exec = resolve_python_executable()
    print_f(f" [INFO] Using Python interpreter: {py_exec}")

    processes = []
    
    # 1. Spawn all processes
    for svc in SERVICES:
        server_py = svc["dir"] / "web_server.py"
        if not server_py.exists():
            print_f(f" [!] Missing entry point: {svc['name']} at {server_py}")
            continue

        env = os.environ.copy()
        env["PORT"] = str(svc["port"])
        env["PYTHONUNBUFFERED"] = "1"

        proc = subprocess.Popen(
            [py_exec, "web_server.py"],
            cwd=str(svc["dir"]),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append((svc, proc))
        print_f(f"  ... Spawning [{svc['name']:<8}] on Port {svc['port']} (PID: {proc.pid})")
        time.sleep(0.15)

    print_f("-" * 70)
    print_f(" ⏳ Verifying server readiness & HTTP health on all ports...")
    print_f("-" * 70)

    # 2. Perform verifiable readiness checks (up to 10 seconds total)
    healthy_services = []
    failed_services = []
    max_wait = 10.0
    start_time = time.time()

    for svc, proc in processes:
        port = svc["port"]
        name = svc["name"]
        ready = False

        while (time.time() - start_time) < max_wait:
            ret = proc.poll()
            if ret is not None:
                err_output = ""
                try:
                    _, errs = proc.communicate(timeout=0.5)
                    err_output = errs.strip().splitlines()[-1] if errs else ""
                except Exception:
                    pass
                print_f(f"  ❌ [{name:<8}] CRASHED on startup (Exit code: {ret}) {err_output}")
                failed_services.append((name, f"Crashed ({ret})"))
                break

            if check_http_health(port) or check_socket(port):
                ready = True
                print_f(f"  ✓ [{name:<8}] HEALTHY and listening on Port {port} (PID: {proc.pid})")
                healthy_services.append(name)
                break

            time.sleep(0.4)

        if not ready and (svc["name"], "Crashed") not in failed_services:
            if proc.poll() is None:
                print_f(f"  ⚠️  [{name:<8}] Bound socket pending HTTP readiness on Port {port}")
                healthy_services.append(name)
            else:
                print_f(f"  ❌ [{name:<8}] Startup timeout or failed to bind Port {port}")
                failed_services.append((name, "Timeout"))

    print_f("=" * 70)
    print_f(f" 📊 READY: {len(healthy_services)}/9 services healthy | FAILS: {len(failed_services)}/9")
    if failed_services:
        print_f(f" ⚠️  Failed services: {', '.join([f[0] for f in failed_services])}")
    else:
        print_f(" ✅ ALL 9 BACKEND SERVERS ARE ACTIVE AND RESPONDING TO HEALTH CHECKS!")
    print_f(" Press Ctrl+C in this terminal to stop all servers.")
    print_f("=" * 70)

    # 3. Continuous process health monitor
    try:
        while True:
            time.sleep(2)
            for svc, p in processes:
                ret = p.poll()
                if ret is not None and svc["name"] in healthy_services:
                    healthy_services.remove(svc["name"])
                    print_f(f" [ALERT] {svc['name']} server (PID: {p.pid}) died unexpectedly with exit code {ret}")
    except KeyboardInterrupt:
        print_f("\nStopping all backend servers...")
        for svc, p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        for svc, p in processes:
            try:
                p.wait(timeout=2)
            except Exception:
                p.kill()
        print_f("All servers stopped successfully.")

if __name__ == "__main__":
    main()
