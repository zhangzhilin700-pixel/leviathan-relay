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

if __name__ == "__main__":
    main()
