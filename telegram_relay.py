#!/usr/bin/env python3
"""
利維坦軍團 · 王國信使 (telegram_relay.py)
用途：接收 Telegram 指令，轉發給 leviathan.sh tool
"""

import requests
import subprocess
import time

TOKEN = "8873521783:AAGkCViluau5d6hdkDwfe683CjThGX1HKcc"
URL = f"https://api.telegram.org/bot{TOKEN}/"
LAST_UPDATE = 0

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text})

def main():
    global LAST_UPDATE
    print("🐋 利維坦王國信使啟動，等待指令...")
    while True:
        try:
            resp = requests.get(URL + "getUpdates", params={"offset": LAST_UPDATE + 1, "timeout": 30})
            for update in resp.json().get("result", []):
                LAST_UPDATE = update["update_id"]
                msg = update.get("message")
                if msg and "text" in msg:
                    chat_id = msg["chat"]["id"]
                    text = msg["text"]
                    if text.startswith("/cmd"):
                        cmd = text[4:].strip()
                        result = subprocess.run(["/home/wangguo-2026/leviathan.sh", "tool", cmd], capture_output=True, text=True)
                        send_message(chat_id, result.stdout or "✅ 指令已執行")
        except Exception as e:
            print(f"⚠️ 錯誤: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()
EOF

