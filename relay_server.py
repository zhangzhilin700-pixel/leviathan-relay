from flask import Flask, request, jsonify
import os
import json
import hmac
import hashlib
import requests
import threading

app = Flask(__name__)

# === 環境變數 ===
SECRET_KEY = os.environ.get('LEVIATHAN_SECRET', 'leviathan_test_secret_2026').encode()
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

# === 啟動檢查（這些會出現在 Render Logs）===
print("=" * 50)
print("🚀 利維坦王室信使啟動中...")
print(f"📋 TELEGRAM_TOKEN 是否存在: {'是' if TELEGRAM_TOKEN else '否'}")
print(f"📋 TELEGRAM_TOKEN 前10碼: {TELEGRAM_TOKEN[:10] if TELEGRAM_TOKEN else '空'}")
print(f"📋 SECRET_KEY 前10碼: {SECRET_KEY[:10] if SECRET_KEY else '空'}")
print("=" * 50)

# === 安全驗證 ===
def verify_signature(payload, signature):
    message = json.dumps(payload, sort_keys=True)
    expected = hmac.new(SECRET_KEY, message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# === 非同步發送訊息（完整偵錯）===
def async_send_message(chat_id, text):
    print(f"🔍 [發送] 嘗試發送訊息給 {chat_id}")
    if not TELEGRAM_TOKEN:
        print("❌ [發送] TELEGRAM_TOKEN 是空的！")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={'chat_id': chat_id, 'text': text}, timeout=5)
        print(f"📤 [發送] HTTP {resp.status_code}")
        if resp.status_code == 200:
            print("✅ [發送] 訊息發送成功！")
        else:
            print(f"❌ [發送] 錯誤: {resp.text}")
    except Exception as e:
        print(f"❌ [發送] 例外: {e}")

# === 路由 ===
@app.route('/')
def root():
    return jsonify({
        "service": "利維坦王室信使",
        "status": "alive",
        "version": "2.0-debug",
        "endpoints": {
            "health": "/health",
            "relay": "/api/relay (POST)",
            "webhook": "/webhook (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive"})

@app.route('/api/relay', methods=['POST'])
def relay():
    data = request.get_json()
    if not data or 'payload' not in data or 'signature' not in data:
        return jsonify({"status": "error", "message": "invalid request"}), 400
    if not verify_signature(data['payload'], data['signature']):
        return jsonify({"status": "error", "message": "unauthorized"}), 401
    return jsonify({"status": "success", "message": "王令已達", "echo": data['payload']})

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    print("🔔 [Webhook] 收到 POST 請求")
    update = request.get_json(silent=True)
    if not update:
        print("❌ [Webhook] 無法解析 JSON")
        return 'OK', 200
    if 'message' not in update:
        print(f"📭 [Webhook] 忽略非訊息更新: {update}")
        return 'OK', 200
    
    chat_id = update['message']['chat']['id']
    user_text = update['message'].get('text', '')
    print(f"📨 [Webhook] 來自 {chat_id}: {user_text}")
    
    if user_text.startswith('/cmd '):
        command = user_text[5:]
        response_text = f"✨ 王令已收到：{command}\n正在傳達給王權之手..."
    else:
        response_text = "⚡ 歡迎蒞臨利維坦王國。\n請輸入 /cmd 你的指令 來發號施令。"
    
    print(f"💬 [Webhook] 回應: {response_text[:50]}...")
    threading.Thread(target=async_send_message, args=(chat_id, response_text)).start()
    print("✅ [Webhook] 已啟動非同步發送線程")
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 監聽埠: {port}")
    app.run(host='0.0.0.0', port=port)
