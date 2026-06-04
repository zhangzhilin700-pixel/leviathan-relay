from flask import Flask, request, jsonify
import os
import json
import hmac
import hashlib

app = Flask(__name__)

SECRET_KEY = os.environ.get('LEVIATHAN_SECRET', 'leviathan_test_secret_2026').encode()

def verify_signature(payload, signature):
    message = json.dumps(payload, sort_keys=True)
    expected = hmac.new(SECRET_KEY, message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route('/api/relay', methods=['POST'])
def relay():
    data = request.get_json()
    if not data or 'payload' not in data or 'signature' not in data:
        return jsonify({"status": "error", "message": "invalid request"}), 400
    if not verify_signature(data['payload'], data['signature']):
        return jsonify({"status": "error", "message": "unauthorized"}), 401
    return jsonify({"status": "success", "message": "王令已達", "echo": data['payload']})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive"})
@app.route('/')
def root():
    return jsonify({
        "service": "利維坦王室信使",
        "status": "alive",
        "endpoints": {
            "health": "/health",
            "relay": "/api/relay (POST)"
        },
        "message": "王令已達，信使待命"
    })
# --- Telegram 設定 ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://leviathan-relay.onrender.com')

def send_telegram_message(chat_id, text):
    if not TELEGRAM_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        import requests
        requests.post(url, json={'chat_id': chat_id, 'text': text}, timeout=3)
    except Exception as e:
        print(f"傳送失敗: {e}")

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if not update or 'message' not in update:
        return 'OK', 200
    
    chat_id = update['message']['chat']['id']
    user_text = update['message'].get('text', '')
    
    if user_text.startswith('/cmd '):
        command = user_text[5:]
        response_text = f"✨ 王令已收到：{command}\n正在傳達給王權之手..."
    else:
        response_text = "⚡ 歡迎蒞臨利維坦王國。\n請輸入 /cmd 你的指令 來發號施令。"
    
    send_telegram_message(chat_id, response_text)
    return 'OK', 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
