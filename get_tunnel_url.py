import subprocess
import re
import sys
import time
from pathlib import Path

BASE_DIR = Path(r"C:\Users\nasee\Desktop\marketing-ai-agent")
CLOUDFLARED = BASE_DIR / "cloudflared.exe"
URL_FILE = BASE_DIR / "live_public_url.txt"

print("[START] Launching Cloudflare Tunnel loop...")

while True:
    try:
        proc = subprocess.Popen(
            [str(CLOUDFLARED), "tunnel", "--url", "http://127.0.0.1:8800"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if m:
                found_url = m.group(0)
                print("\n" + "="*50)
                print(f"FOUND_URL:{found_url}")
                print("="*50 + "\n")
                URL_FILE.write_text(found_url, encoding="utf-8")
                # Do not exit, keep process alive so the tunnel stays open!
                proc.wait()

        # If it exited without URL, wait 2 sec and retry
        time.sleep(2)
    except Exception as e:
        print("[ERROR]", e)
        time.sleep(2)
