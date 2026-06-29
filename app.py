import threading
import time
import requests
import subprocess
import os
from flask import Flask

# 1. 基礎設定
TOKEN = "8873521783:AAGkCViluau5d6hdkDwfe683CjThGX1HKcc"
URL = f"https://api.telegram.org/bot{TOKEN}/"
LAST_UPDATE = 0
app_web = Flask(__name__)

# 2. 核心通訊功能
def send_message(chat_id, text):
    try:
        requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"❌ 發送失敗: {e}")

# 3. 輪詢主程式 (Polling)
def main():
    global LAST_UPDATE
    print("🐋 利維坦王國信使啟動，等待指令...")
    # 強制清除 Webhook，奪回控制權
    requests.get(URL + "deleteWebhook")
    
    while True:
        try:
            resp = requests.get(URL + "getUpdates", params={"offset": LAST_UPDATE + 1, "timeout": 30})
            data = resp.json()
            for update in data.get("result", []):
                LAST_UPDATE = update["update_id"]
                msg = update.get("message")
                if msg and "text" in msg:
                    chat_id = msg["chat"]["id"]
                    text = msg["text"]
                    if text.startswith("/cmd"):
                        # 執行指令邏輯
                        result = subprocess.run(["./leviathan.sh", "tool", text[4:].strip()], capture_output=True, text=True)
                        send_message(chat_id, result.stdout.strip() or "✅ 指令執行完畢")
        except Exception as e:
            print(f"⚠️ 運行錯誤: {e}")
        time.sleep(1)

# 4. Web 監聽器 (滿足 Render 需求)
@app_web.route('/')
def home():
    return "利維坦王國信使：Polling 模式運作中", 200

if __name__ == "__main__":
    threading.Thread(target=main, daemon=True).start()
    app_web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
