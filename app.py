#!/usr/bin/env python3
"""
利維坦軍團 · 戰情室（Gradio 公開版）
僅顯示運算邏輯與公開數據，不含司令身份與敏感日誌
"""

import gradio as gr
import subprocess
import re
import json
from datetime import datetime

def get_system_status():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        chat_status = "🟢 在線" if "leviathan-chat" in result.stdout else "🔴 離線"
        pure_status = "🟢 在線" if "leviathan-pure" in result.stdout else "🔴 離線"
        return chat_status, pure_status
    except:
        return "⚪ 無法偵測", "⚪ 無法偵測"

def fetch_report_data():
    result = subprocess.run(["python", "daily_report.py"], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    projects = []
    for line in lines:
        if "✅" in line:
            match = re.search(r'✅ (\S+).*?(\d+\.?\d*)', line)
            if match:
                projects.append(f"{match.group(1)}：預估需 {match.group(2)} 天")
    return "\n".join(projects) if projects else "無專案數據"

def dashboard_view():
    chat, pure = get_system_status()
    projects = fetch_report_data()
    return f"""
    🐋 利維坦軍團 · 公開戰情室

    🗣️ 聊天港: {chat}
    💻 算力港: {pure}

    📊 專案進度:
    {projects}

    更新時間: {datetime.now().isoformat()}
    """

iface = gr.Interface(
    fn=dashboard_view,
    inputs=[],
    outputs="text",
    title="利維坦軍團 · 公開戰情室",
    description="僅顯示運算邏輯與公開數據，不含敏感資訊"
)

if __name__ == "__main__":
    iface.launch()
