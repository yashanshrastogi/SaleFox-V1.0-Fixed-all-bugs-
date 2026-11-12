import os
import sys
import subprocess
import time
import socket

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BATCH_PATH = os.path.join(PROJECT_ROOT, "start_frontend.bat")

test_dirs = [
    ("1. SaleFox Project Root", PROJECT_ROOT),
    ("2. Parent Directory", os.path.dirname(PROJECT_ROOT)),
    ("3. Unrelated User Profile Directory", os.path.expanduser("~")),
    ("4. Windows Temp Directory", os.environ.get("TEMP", "C:\\Windows\\Temp"))
]

def run_tests():
    all_passed = True
    for name, test_cwd in test_dirs:
        print(f"\n--- Testing from: {name} ({test_cwd}) ---")
        
        proc = subprocess.Popen(
            [BATCH_PATH],
            cwd=test_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        started = False
        start_time = time.time()
        
        while time.time() - start_time < 8:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            res = s.connect_ex(("127.0.0.1", 5173))
            s.close()
            if res == 0:
                started = True
                break
            time.sleep(0.5)
            
        print(f"Result: {'PASS' if started else 'FAIL'} (took {time.time() - start_time:.2f}s)")
        
        # Terminate
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
            
        # Cleanup any node.exe listening on 5173
        subprocess.run(["powershell", "-Command", "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"], capture_output=True)
        time.sleep(1)
        
        if not started:
            all_passed = False

    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

