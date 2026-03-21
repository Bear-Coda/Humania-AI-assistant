from llama_cpp import Llama
import os
import sys

def get_path(rel_path):
    """Finds files whether we are running the script or the final .exe"""
    if hasattr(sys, '_MEIPASS'):
        # When running as EXE, files are in a temporary folder
        return os.path.join(sys._MEIPASS, rel_path)
    
    # When running as a script, looks in the current folder
    # Note: We will point this to the 'assets' folder you create
    return os.path.join(os.path.abspath("."), rel_path)

# Correctly locate the model inside the 'assets/models' folder
MODEL_PATH = get_path(os.path.join("assets", "models", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"))

try:
    # We use MODEL_PATH here so it finds the brain on any computer
    llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4, verbose=False)
except Exception:
    llm = None

def get_ai_response_stream(chat_history, params):
    if llm is None:
        yield "Error: Brain not found. Please check the assets/models folder."
        return
    
    bot_name = params.get('name', 'Bob')
    gender = "male" if params.get('is_male', True) else "female"
    description = params.get('persona', 'a friendly human.')
    
    system_message = f"Your name is {bot_name}. You are a {gender} and you are {description}"
    full_prompt = f"<|system|>\n{system_message}</s>\n"
    
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            full_prompt += f"<|user|>\n{content}</s>\n"
        else:
            full_prompt += f"<|assistant|>\n{content}</s>\n"
            
    full_prompt += "<|assistant|>\n"
    
    stream = llm(
        full_prompt, 
        max_tokens=int(params.get('length', 256)), 
        stop=["</s>", "You:", "<|user|>", "<|system|>"], 
        stream=True,
        temperature=float(params.get('creativity', 70)) / 100,
        top_p=float(params.get('focus', 90)) / 100,
        repeat_penalty=float(params.get('repetition', 110)) / 100
    )
    
    for chunk in stream:
        if "choices" in chunk:
            yield chunk["choices"][0]["text"]