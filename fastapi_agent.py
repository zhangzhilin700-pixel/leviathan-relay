import os
import json
import logging
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leviathan Fleet Commander", version="1.3.0")

class AgentCommand(BaseModel):
    task: str

def call_model(model_name: str, prompt: str) -> str:
    try:
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
    except Exception as e:
        logger.error(f"模型 {model_name} 呼叫失敗: {e}")
        return f"Error: {e}"

def extract_models_from_response(text: str) -> list:
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            if "models" in data:
                return data["models"]
    except:
        pass
    models = []
    if "deepseek-math" in text.lower():
        models.append("deepseek-math")
    if "leviathan-pure" in text.lower():
        models.append("leviathan-pure")
    return models

def save_generated_file(filename: str, content: str) -> dict:
    """將生成的內容儲存為檔案"""
    os.makedirs("./generated", exist_ok=True)
    filepath = f"./generated/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return {"status": "success", "filepath": filepath}

@app.post("/fleet/execute")
async def fleet_execute(command: AgentCommand):
    try:
        logger.info(f"📥 艦隊接收任務: {command.task}")

        commander_prompt = f"""
        任務: {command.task}
        指揮準則：
        1. 嚴禁親自執行數學運算，請調用 'deepseek-math'。
        2. 嚴禁親自編寫程式碼，請調用 'leviathan-pure'。
        3. 必須將上述兩個模組放入 models 列表。
        回傳嚴格的 JSON 格式：
        {{"models": ["deepseek-math", "leviathan-pure"], "reasoning": "執行分發任務"}}
        """
        plan_response = call_model("leviathan-9B-MoE", commander_prompt)
        models = extract_models_from_response(plan_response)

        results = {}
        for model_name in models:
            if model_name == "deepseek-math":
                results["math"] = call_model("deepseek-math", f"請處理以下任務: {command.task}")
            elif model_name == "leviathan-pure":
                results["pure"] = call_model("leviathan-pure", f"請為以下任務生成 Python 程式碼: {command.task}")

        final_prompt = f"""
        原始任務: {command.task}
        各模型回饋: {json.dumps(results, ensure_ascii=False)}
        請整合這些資訊，以【分析】→【判斷】→【行動】的結構，生成最終回應。
        """
        final_response = call_model("leviathan-9B-MoE", final_prompt)

        # --- 新增自動儲存功能 ---
        file_saved = False
        if "pure" in results:
            # 嘗試從 leviathan-pure 的回應中提取程式碼
            code_content = results["pure"]
            # 簡單判斷：若內容包含 def 或 import，視為 Python 程式碼
            if "def " in code_content or "import " in code_content:
                save_result = save_generated_file("generated_code.py", code_content)
                file_saved = True
                logger.info(f"💾 程式碼已自動儲存: {save_result['filepath']}")

        return {
            "status": "success",
            "task": command.task,
            "plan": {"models": models, "reasoning": "解析成功" if models else "預設流程"},
            "results": results,
            "final_response": final_response,
            "file_saved": file_saved
        }

    except Exception as e:
        logger.error(f"❌ 錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
