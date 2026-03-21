import os
import requests

os.makedirs("models", exist_ok=True)
url = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
output_path = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

# Check if we already have a partial file
existing_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

# If the file is already the right size, stop here
if existing_size >= 669144384:
    print("✅ File is already complete!")
else:
    print(f"Resuming download from {existing_size / (1024**2):.2f} MB...")
    headers = {"Range": f"bytes={existing_size}-"}
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        # 206 means 'Partial Content' - exactly what we want
        mode = "ab" if response.status_code == 206 else "wb"
        
        with open(output_path, mode) as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("✅ Download complete!")
    except Exception as e:
        print(f"❌ Connection lost again. Just run the script one more time to continue! Error: {e}")