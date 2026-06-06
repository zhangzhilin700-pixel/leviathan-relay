from flask import Flask, request, jsonify
import os
import json
import hmac
import hashlib
import requests
import threading

app = Flask(__name__)

# --- 環境變數設定 ---
SECRET_KEY = os.environ.get('LEVIATHAN_SECRET', 'leviathan_test_secret_2026').encode()
# 從 Secret File 讀取 Telegram Token
try:
    with open('/etc/secrets/telegram_token.txt', 'r') as f:
        TELEGRAM_TOKEN = f.read().strip()
        print(f"📋 已從 Secret File 讀取 Token，長度: {len(TELEGRAM_TOKEN)}")
except Exception as e:
    TELEGRAM_TOKEN = ''
    print(f"❌ 無法讀取 Secret File: {e}")

# --- 啟動檢查（寫入 Logs）---
print("=" * 50)
print("🚀 利維坦王室信使啟動中...")
print(f"📋 TELEGRAM_TOKEN 已設定: {'是' if TELEGRAM_TOKEN else '否'}")
print(f"📋 SECRET_KEY 已設定: {'是' if SECRET_KEY else '否'}")
print("=" * 50)

# --- 安全驗證 ---
def verify_signature(payload, signature):
    message = json.dumps(payload, sort_keys=True)
    expected = hmac.new(SECRET_KEY, message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# --- 非同步處理函式 ---
def async_send_message(chat_id, text):
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN 是空的，無法發送訊息")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={'chat_id': chat_id, 'text': text}, timeout=5)
        if resp.status_code == 200:
            print(f"✅ 訊息已發送給 {chat_id}")
        else:
            print(f"❌ 發送失敗: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ 例外: {e}")

# --- 路由配置 ---
@app.route('/')
def root():
    return jsonify({
        "status": "alive",
        "service": "利維坦王室信使",
        "version": "1.0.0"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive"})

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    print("🔔 Webhook 收到請求")
    update = request.get_json(silent=True)
    if not update or 'message' not in update:
        return 'OK', 200
    
    chat_id = update['message']['chat']['id']
    user_text = update['message'].get('text', '')
    print(f"📨 來自 {chat_id}: {user_text}")
    
    if user_text.startswith('/cmd '):
    command = user_text[5:]
    
    if user_text.startswith('/cmd '):
    command = user_text[5:] 

    # 處理 svg2png 王令
    if command.startswith("svg2png "):
        svg_file = command.split(" ")[1]
        import subprocess
        result = subprocess.run(["inkscape", svg_file, "--export-filename=" + svg_file.replace(".svg", ".png")])
        if result.returncode == 0:
            response_text = f"🎨 已將 {svg_file} 轉換為 PNG"
        else:
            response_text = f"❌ 轉換失敗，請檢查檔案路徑：{svg_file}"
    else:
        response_text = f"✨ 王令已收到：{command}\n利維坦正在執行內部演算..."
    
    threading.Thread(target=async_send_message, args=(chat_id, response_text)).start()
    return 'OK', 200

@app.route('/api/relay', methods=['POST'])
def relay():
    data = request.get_json()
    if not data or 'payload' not in data or 'signature' not in data:
        return jsonify({"status": "error"}), 400
    if not verify_signature(data['payload'], data['signature']):
        return jsonify({"status": "unauthorized"}), 401
    return jsonify({"status": "success", "echo": data['payload']})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 監聽埠: {port}")
    app.run(host='0.0.0.0', port=port)
