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
@app.route('/')
def root():
    return jsonify({"status": "alive", "message": "利維坦王室信使已甦醒"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
