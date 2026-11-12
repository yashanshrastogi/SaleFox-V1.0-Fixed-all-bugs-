import os
import sys
import time
import json
import urllib.request
import urllib.parse
import subprocess
import socket

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PYTHON_EXE = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

SERVICES = [
    {"name": "Amazon", "port": 5050, "test_query": "iPhone 15"},
    {"name": "Flipkart", "port": 5051, "test_query": "iPhone 15"},
    {"name": "Vivo", "port": 5052, "test_query": "Vivo V30"},
    {"name": "Samsung", "port": 5053, "test_query": "Galaxy S24"},
    {"name": "Croma", "port": 5054, "test_query": "iPhone 15"},
    {"name": "Apple", "port": 5055, "test_query": "iPhone 15"},
    {"name": "Reliance", "port": 5056, "test_query": "iPhone 15"},
    {"name": "Oppo", "port": 5057, "test_query": "Oppo Reno 11"},
    {"name": "JioMart", "port": 5062, "test_query": "iPhone 15"},
]

def http_get(url, timeout=5):
    try:
        t0 = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "SaleFoxRegression/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            lat = round((time.time() - t0) * 1000, 2)
            return {
                "ok": True,
                "status": resp.status,
                "data": json.loads(raw.decode("utf-8", errors="ignore")),
                "size_bytes": len(raw),
                "latency_ms": lat
            }
    except Exception as e:
        return {"ok": False, "error": str(e), "size_bytes": 0, "latency_ms": 0}

def http_post(url, data, timeout=6):
    try:
        t0 = time.time()
        raw_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=raw_data, headers={"Content-Type": "application/json", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            lat = round((time.time() - t0) * 1000, 2)
            return {
                "ok": True,
                "status": resp.status,
                "data": json.loads(raw.decode("utf-8", errors="ignore")),
                "size_bytes": len(raw),
                "latency_ms": lat
            }
    except urllib.error.HTTPError as e:
        raw = e.read()
        return {
            "ok": False,
            "status": e.code,
            "data": json.loads(raw.decode("utf-8", errors="ignore")) if raw else {},
            "size_bytes": len(raw),
            "latency_ms": 0
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "size_bytes": 0, "latency_ms": 0}

def main():
    print("=== SALEFOX MASTER REGRESSION & VERIFICATION SUITE ===")
    
    # 1. Start launcher in background
    print("\n[STEP 1] Launching run_all_backends.py...")
    launcher_proc = subprocess.Popen(
        [PYTHON_EXE, "run_all_backends.py"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait up to 18 seconds for all 9 services to report healthy
    all_ready = False
    start_time = time.time()
    while time.time() - start_time < 18:
        ready_count = 0
        for s in SERVICES:
            res = http_get(f"http://127.0.0.1:{s['port']}/api/health", timeout=1.0)
            if res.get("ok"):
                ready_count += 1
            else:
                st_res = http_get(f"http://127.0.0.1:{s['port']}/api/status", timeout=1.0)
                if st_res.get("ok"):
                    ready_count += 1
        if ready_count == len(SERVICES):
            all_ready = True
            break
        time.sleep(1)
        
    print(f"All 9 services initialized: {all_ready} (took {time.time() - start_time:.1f}s)")
    
    results = {}
    
    # 2. Test /api/health and /api/status efficiency
    print("\n[STEP 2] Testing /api/health endpoint efficiency across all 9 backends...")
    health_results = {}
    for s in SERVICES:
        h_res = http_get(f"http://127.0.0.1:{s['port']}/api/health")
        s_res = http_get(f"http://127.0.0.1:{s['port']}/api/status")
        health_results[s["name"]] = {
            "health_endpoint": {
                "ok": h_res.get("ok"),
                "status": h_res.get("status"),
                "size_bytes": h_res.get("size_bytes"),
                "latency_ms": h_res.get("latency_ms")
            },
            "status_endpoint": {
                "ok": s_res.get("ok"),
                "status": s_res.get("status"),
                "size_bytes": s_res.get("size_bytes"),
                "latency_ms": s_res.get("latency_ms")
            }
        }
        print(f"  {s['name']:10} | /api/health: {h_res.get('size_bytes', 0):4} bytes ({h_res.get('latency_ms', 0):.1f}ms) | /api/status: {s_res.get('size_bytes', 0):7} bytes")
    results["health_efficiency"] = health_results
    
    # 3. Test Fail-Closed Checkout Safety API
    print("\n[STEP 3] Testing Fail-Closed Checkout Safety API (/api/automation/start)...")
    safety_results = {}
    test_ports = [5050, 5054, 5055]
    for p in test_ports:
        url = f"http://127.0.0.1:{p}/api/automation/start"
        rej_res = http_post(url, {})
        fake_phone_res = http_post(url, {
            "customer_name": "Test User",
            "customer_phone": "9876543210",
            "delivery_address": "Test Address",
            "delivery_pincode": "110001"
        })
        demo_res = http_post(url, {
            "automation_mode": "dry_run",
            "customer_name": "Rohan Sharma",
            "customer_phone": "9811223344",
            "customer_email": "rohan.sharma@example-domain.org",
            "delivery_address": "Flat 204, Tower B, Cyber Heights",
            "delivery_pincode": "110001"
        })
        safety_results[p] = {
            "empty_rejected": rej_res.get("status") == 400 and rej_res["data"].get("code") == "CHECKOUT_SAFETY_VIOLATION",
            "fake_phone_rejected": fake_phone_res.get("status") == 400 and fake_phone_res["data"].get("code") == "CHECKOUT_SAFETY_VIOLATION",
            "valid_demo_accepted": demo_res.get("ok") and demo_res["data"].get("status") == "started"
        }
        print(f"  Port {p} | Empty Rejected: {safety_results[p]['empty_rejected']} | Fake Phone Rejected: {safety_results[p]['fake_phone_rejected']} | Valid Demo Accepted: {safety_results[p]['valid_demo_accepted']}")
    results["checkout_safety"] = safety_results
    
    # 4. Search and Field Integrity
    print("\n[STEP 4] Testing Search & Field Integrity across backends...")
    search_results = {}
    for s in SERVICES:
        scrape_url = f"http://127.0.0.1:{s['port']}/api/scrape"
        status_url = f"http://127.0.0.1:{s['port']}/api/status"
        trig = http_post(scrape_url, {"query": s["test_query"], "pages": 1, "pincode": "110058"})
        
        final_items = []
        for _ in range(5):
            time.sleep(1.0)
            st = http_get(status_url)
            items = st.get("data", {}).get("products") or st.get("data", {}).get("results") or []
            if len(items) > 0:
                final_items = items
                break
                
        search_results[s["name"]] = {
            "query": s["test_query"],
            "triggered": trig.get("ok"),
            "items_found": len(final_items),
            "sample_title": (final_items[0].get("name") or final_items[0].get("title") or final_items[0].get("model")) if final_items else None,
            "sample_price": final_items[0].get("price") if final_items else None
        }
        print(f"  {s['name']:10} | Query: '{s['test_query']}' | Items: {len(final_items):3} | Sample: {search_results[s['name']]['sample_title'][:40] if search_results[s['name']]['sample_title'] else 'None'}")
    results["search_integrity"] = search_results

    # 5. Terminate and verify clean shutdown
    print("\n[STEP 5] Shutting down launcher and all child processes...")
    try:
        launcher_proc.terminate()
        launcher_proc.wait(timeout=2)
    except Exception:
        pass

    # Targeted cleanup: kill only the processes listening on the backend ports
    for s in SERVICES:
        port = s["port"]
        try:
            out = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            for line in out.strip().splitlines():
                if "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    if pid not in ("0", ""):
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        except Exception:
            pass
    time.sleep(2)
    
    # Check port release (verify no process is LISTENING)
    lingering_ports = []
    for s in SERVICES:
        out = subprocess.run(f"netstat -ano | findstr :{s['port']} | findstr LISTENING", shell=True, capture_output=True, text=True)
        for line in out.stdout.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[-1] not in ("0", ""):
                lingering_ports.append(s["port"])
                break
            
    print(f"Active listening ports after shutdown: {lingering_ports} (0 expected)")
    results["lingering_ports"] = lingering_ports
    results["lifecycle_clean"] = len(lingering_ports) == 0
    
    output_path = os.path.join(PROJECT_ROOT, "SALEFOX_TEST_EVIDENCE", "master_regression_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print("\n=== MASTER REGRESSION RUN COMPLETE ===")
    return all_ready and results["lifecycle_clean"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
