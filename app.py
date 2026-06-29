#!/usr/bin/env python3
import requests
import subprocess
import time

# 請確保此處 Token 正確
TOKEN = "8873521783:AAGkCViluau5d6hdkDwfe683CjThGX1HKcc"
URL = f"https://api.telegram.org/bot{TOKEN}/"
LAST_UPDATE = 0

def send_message(chat_id, text):
    try:
        requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"❌ 發送失敗: {e}")

def main():
    global LAST_UPDATE
    print("🐋 利維坦王國信使啟動，等待指令...")
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
                    print(f"📡 收到指令: {text}")
                    
                    # 指令分發邏輯
                    if text.startswith("/cmd"):
                        cmd_args = text[4:].strip().split(" ", 1)
                        if len(cmd_args) < 2:
                            send_message(chat_id, "⚠️ 格式錯誤。請使用: /cmd [algo|tool] [參數]")
                            continue
                        
                        mode, arg = cmd_args[0], cmd_args[1]
                        # 呼叫統籌腳本
                        result = subprocess.run(["/home/wangguo-2026/leviathan_core/leviathan.sh", mode, arg], capture_output=True, text=True)
                        reply = result.stdout.strip() or "✅ 指令執行完畢，無回傳輸出。"
                        send_message(chat_id, f"🐋 利維坦回報:\n{reply}")
        except Exception as e:
            print(f"⚠️ 運行錯誤: {e}")
        time.sleep(1)

import threading
from flask import Flask

# 初始化 Flask 應用
app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "利維坦王國信使：狀態正常 (Online)", 200

def run_web():
    # Render 要求的端口通常在環境變數 PORT 中
    import os
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # 1. 啟動 Telegram 輪詢 (維持原有的 main 函數)
    threading.Thread(target=main, daemon=True).start()
    # 2. 啟動 Web 服務以滿足 Render 部署要求
    run_web()
    
if __name__ == "__main__":
    main()

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update or 'message' not in update:
        return "OK", 200
    chat_id = update['message']['chat']['id']
    text = update['message'].get('text', '')
    if text.startswith('/cmd'):
        import subprocess
        cmd = text[4:].strip()
        result = subprocess.run(['/home/wangguo-2026/leviathan.sh', 'tool', cmd], capture_output=True, text=True)
        reply = result.stdout or "✅ 指令已執行"
        send_message(chat_id, reply)
    return "OK", 200
