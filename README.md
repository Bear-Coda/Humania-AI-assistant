# Humania AI Assistant

A local desktop AI assistant built with Python and Flet, with animated ASCII character output, chat history, and local LLM inference.

## What is included in this repository

- Application source code (`main.py`, UI logic, DB logic, voice logic)
- Assets needed for UI (images/icons/logos)
- Setup instructions for running the project locally

## What is NOT included

To keep the GitHub repository lightweight, the following are excluded:

- Local LLM model files (for example `.gguf`)
- Virtual environment folders (`.venv`, `venv`, etc.)
- Built binaries and packaging folders (`dist`, `build`)

## Requirements

- Python 3.10+ (recommended)
- Windows (recommended for matching current TTS voices and EXE build flow)

## Installation (developer mode)

1. Clone the repository:
   - `git clone <your-repo-url>`
   - `cd "AI face"`
2. Create and activate a virtual environment:
   - `python -m venv .venv`
   - `.\.venv\Scripts\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`

## Download and place the LLM model

This project expects the model at:

- `assets/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`

Steps:

1. Create folder `assets/models` if it does not exist.
2. Download the model file manually from your trusted source.
3. Place the file exactly at the path above.

If the model is missing, the app will run but AI replies will show an error message.

## Run the app

- `python main.py`

## Optional: build EXE later

You can publish the EXE in a later GitHub release.

Typical local build flow:

- `pyinstaller --noconfirm --onefile --windowed main.py`

After building, the executable is usually inside `dist/`.

## Notes

- Chat/user data is stored locally in `app_data.db`.
- Do not upload private data or local model files.
- If you want to share the EXE later, use GitHub Releases (recommended).

