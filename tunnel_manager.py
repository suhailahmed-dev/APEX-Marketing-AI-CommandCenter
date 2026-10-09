import subprocess
import re
import sys
import time
import socket
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent.resolve()
CLOUDFLARED_EXE = BASE_DIR / "cloudflared.exe"
URL_FILE = BASE_DIR / "CLIENT_TEST_LINK.txt"
LIVE_URL_FILE = BASE_DIR / "live_public_url.txt"
PORT = 8800

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def ensure_dashboard_running():
    if not is_port_in_use(PORT):
        print(f"[SYSTEM] Starting Dashboard server on port {PORT}...", flush=True)
        subprocess.Popen(
            [sys.executable, str(BASE_DIR / "dashboard.py")],
            cwd=str(BASE_DIR),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        for _ in range(15):
            time.sleep(1)
            if is_port_in_use(PORT):
                print(f"[SYSTEM] Dashboard is now online at http://127.0.0.1:{PORT}", flush=True)
                break
    else:
        print(f"[SYSTEM] Dashboard is already running on http://127.0.0.1:{PORT}", flush=True)

def run_tunnel():
    if not CLOUDFLARED_EXE.exists():
        print(f"[ERROR] cloudflared.exe not found at {CLOUDFLARED_EXE}", flush=True)
        return

    ensure_dashboard_running()

    max_retries = 8
    for attempt in range(1, max_retries + 1):
        print(f"[TUNNEL] Attempt {attempt}/{max_retries}: Starting Cloudflare secure tunnel to http://127.0.0.1:{PORT} ...", flush=True)
        cmd = [str(CLOUDFLARED_EXE), "tunnel", "--url", f"http://127.0.0.1:{PORT}"]
        
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        url_found = None
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                url_found = match.group(0)
                banner = (
                    "\n" + "="*65 + "\n"
                    + ">>> LIVE ONLINE LINK FOR CLIENT TESTING <<<\n"
                    + f"URL: {url_found}\n"
                    + "="*65 + "\n"
                )
                print(banner, flush=True)
                URL_FILE.write_text(
                    f"CLIENT TESTING LINK:\n{url_found}\n\n(Share this URL with your client on WhatsApp. Works on Mobile Phone, Laptop, and Tablet anywhere!)",
                    encoding="utf-8"
                )
                LIVE_URL_FILE.write_text(url_found, encoding="utf-8")
                print(f"Saved link to: {URL_FILE}", flush=True)
                break

        if url_found:
            # Keep tunnel alive
            try:
                proc.wait()
            except KeyboardInterrupt:
                proc.terminate()
            return
        else:
            print(f"[TUNNEL] Connection timed out on attempt {attempt}. Retrying in 2 seconds...", flush=True)
            time.sleep(2)
            try:
                proc.terminate()
            except Exception:
                pass

    print("[TUNNEL] Could not establish quick tunnel after multiple attempts. Please check internet connection.", flush=True)

if __name__ == "__main__":
    run_tunnel()
