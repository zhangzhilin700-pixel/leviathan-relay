#!/bin/bash
# 利維坦軍團 · 具備環境感知能力的調度腳本

case $1 in
    chat)
        # 偵測是否在 Render 環境 (存在 RENDER 環境變數)
        if [ -n "$RENDER" ]; then
            echo "🐋 利維坦（雲端分身）：目前算力受限，無法運行大型模型，但我已準備好執行輕量指令！"
        else
            ollama run leviathan-chat "$2"
        fi
        ;;
    math)
        if [ -n "$RENDER" ]; then
            echo "⚠️ 數學引擎目前僅限地端軍團運作。"
        else
            ollama run deepseek-math "$2"
        fi
        ;;
    # 其餘保持不變...
    *)
        # ... 原內容 ...
        ;;
esac
# 利維坦軍團 · 統一調度腳本
case $1 in
    chat)
        ollama run leviathan-chat "$2"
        ;;
    math)
        ollama run deepseek-math "$2"
        ;;
    tool)
        shift
        python3 ~/leviathan_core/tool_interface.py "$@"
        ;;
    algo)
        shift
        python3 ~/leviathan_core/algorithm_lab.py "$@"
        ;;
    *)
        echo "👑 利維坦軍團指令格式:"
        echo "  ./leviathan.sh chat  \"對話與報告\""
        echo "  ./leviathan.sh math  \"數學推理與工程計算\""
        echo "  ./leviathan.sh tool  \"參數化運算\""
        echo "  ./leviathan.sh algo  \"字串演算法\""
        ;;
esac
