from llama_cpp import Llama
import os
import sys


def get_path(rel_path):
    """Return the correct path in development and PyInstaller builds."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)


def find_model():
    """Find exactly one GGUF model in assets/models."""
    model_dir = get_path(os.path.join("assets", "models"))

    if not os.path.isdir(model_dir):
        raise FileNotFoundError(
            f"Model directory does not exist: {model_dir}"
        )

    models = sorted(
        os.path.join(model_dir, filename)
        for filename in os.listdir(model_dir)
        if filename.lower().endswith(".gguf")
    )

    if not models:
        raise FileNotFoundError(
            f"No GGUF model was found in: {model_dir}"
        )

    if len(models) > 1:
        names = ", ".join(os.path.basename(path) for path in models)
        raise RuntimeError(
            "More than one GGUF model was found. "
            f"Keep only one model in the folder. Found: {names}"
        )

    return models[0]


MODEL_ERROR = None

try:
    MODEL_PATH = find_model()

    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=4096,
        n_threads=max(1, (os.cpu_count() or 4) - 1),
        verbose=False
    )

except Exception as error:
    llm = None
    MODEL_ERROR = str(error)


def get_ai_response_stream(chat_history, params):
    if llm is None:
        yield f"Error loading model: {MODEL_ERROR}"
        return

    bot_name = params.get("name", "Assistant")
    gender = "male" if params.get("is_male", True) else "female"
    persona = params.get("persona", "a friendly and helpful assistant")

    system_message = (
        f"Your name is {bot_name}. "
        f"You have a {gender} identity. "
        f"{persona}"
    )

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    for message in chat_history:
        role = message.get("role", "user")

        if role not in ("user", "assistant", "system"):
            role = "user"

        messages.append(
            {
                "role": role,
                "content": str(message.get("content", ""))
            }
        )

    try:
        stream = llm.create_chat_completion(
            messages=messages,
            max_tokens=max(
                1,
                min(int(params.get("length", 256)), 2048)
            ),
            temperature=max(
                0.0,
                min(float(params.get("creativity", 70)) / 100, 2.0)
            ),
            top_p=max(
                0.05,
                min(float(params.get("focus", 90)) / 100, 1.0)
            ),
            repeat_penalty=max(
                0.8,
                min(float(params.get("repetition", 110)) / 100, 2.0)
            ),
            stream=True
        )

        for chunk in stream:
            choices = chunk.get("choices", [])

            if not choices:
                continue

            delta = choices[0].get("delta", {})
            text = delta.get("content")

            if text:
                yield text

    except Exception as error:
        yield f"Error generating response: {error}"
