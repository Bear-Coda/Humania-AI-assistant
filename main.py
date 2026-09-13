import flet as ft
import char_logic, ai_brain, char_female, db_manager, auth_ui, intro 
from PIL import Image
import asyncio, time, os
import voice_engine 

import sys

def get_path(rel_path):
    """Get the absolute path to the resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)
# Global Image Loads
img_male = Image.open(get_path("assets\\face.jpg")).convert('L')
img_female = Image.open(get_path("assets\\face2.png")).convert('L')

async def main(page: ft.Page):
    # --- WINDOW CONFIGURATION ---
    page.title = "ZerBo6"  # Sets the title of the window
    icon_abs_path = get_path("assets\\icon.ico")
    page.window.icon = icon_abs_path  # Apply the strict pat
    page.window.width = 850
    page.window.height = 520
    page.window.resizable = False      
    page.window.maximizable = False    
    page.theme_mode = ft.ThemeMode.DARK
    
    # Start with the intro
    await intro.show_intro(page)
    
    # Application State
    ai_params = {
        "name": "Bob", "persona": "a real human.", "is_male": True,
        "creativity": 70, "length": 256, "focus": 90,
        "variety": 40, "repetition": 110,
    }
    
    state = {
        "is_talking": False, 
        "last_action_time": time.time(), 
        "running": True, 
        "stop_signal": False,
        "current_user": None,
        "current_chat_id": None
    }

    selected_chats = set()

    # --- UI COMPONENTS ---
    chat_box = ft.Column(scroll="always", expand=True)
    history_list = ft.Column(scroll="always", spacing=10, expand=True)
    
    user_input = ft.TextField(
        hint_text="Type message...", 
        expand=True, multiline=True, min_lines=3, max_lines=3, text_size=14
    )

    # --- LOGIC FUNCTIONS ---
    async def logout(e):
        state["running"] = False 
        state["current_user"] = None
        state["current_chat_id"] = None
        page.clean()
        page.add(auth_ui.show_auth_screen(page, launch_app))
        page.update()

    async def load_old_chat(chat_id):
        state["current_chat_id"] = chat_id
        chat_box.controls.clear()
        messages = db_manager.get_chat_messages(chat_id)
        for role, content in messages:
            lbl = "You: " if role == "user" else f"{ai_params.get('name', 'AI')}: "
            clr = "white" if role == "user" else "blue"
            chat_box.controls.append(ft.Text(f"{lbl}{content}", size=12, color=clr, selectable=True))
        switch_v("chat")
        page.update()

    def on_check_chat(e, chat_id):
        if e.control.value: selected_chats.add(chat_id)
        else: selected_chats.discard(chat_id)

    async def delete_selected(e):
        if not selected_chats: return
        db_manager.delete_chats(list(selected_chats))
        if state["current_chat_id"] in selected_chats:
            state["current_chat_id"] = None
            chat_box.controls.clear()
        selected_chats.clear()
        refresh_history_view()

    async def delete_all(e):
        db_manager.delete_all_user_chats(state["current_user"])
        selected_chats.clear()
        state["current_chat_id"] = None
        chat_box.controls.clear()
        refresh_history_view()

    def refresh_history_view():
        history_list.controls.clear()
        chats = db_manager.get_user_chats(state["current_user"])
        button_width = 400 
        for chat_id, title, created_at in chats:
            is_selected = chat_id in selected_chats
            history_list.controls.append(
                ft.Row([
                    ft.Checkbox(value=is_selected, on_change=lambda e, cid=chat_id: on_check_chat(e, cid)),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{title}", weight="bold", size=14, color="white", max_lines=1),
                            ft.Text(f"📅 {created_at}", size=10, color="grey"),
                        ], spacing=2),
                        padding=12, border=ft.border.all(1, "blue"), border_radius=8, ink=True, width=button_width,
                        on_click=lambda e, cid=chat_id: page.run_task(load_old_chat, cid)
                    )
                ], alignment="start")
            )
        if not chats: history_list.controls.append(ft.Text("No history found.", size=12, italic=True))
        page.update()

    async def forget_context(e):
        state["current_chat_id"] = None
        chat_box.controls.clear()
        chat_box.controls.append(ft.Text("--- New Conversation Started ---", size=10, color="blue", italic=True))
        page.update()

    async def typewriter_add(container, total_text):
        prefix = f"{ai_params['name']}: "
        container.value = prefix
        voice_engine.speak(total_text, state, ai_params["is_male"])
        full_display = ""
        for char in total_text:
            full_display += char
            container.value = prefix + full_display
            await asyncio.sleep(0.03) 
            page.update()
        page.update()

    async def send_msg(e):
        if not user_input.value: return
        if state["current_chat_id"] is None:
            state["current_chat_id"] = db_manager.start_new_chat(state["current_user"])
            chat_box.controls.clear()
        txt = user_input.value
        state["stop_signal"] = False
        db_manager.save_message(state["current_chat_id"], "user", txt)
        raw_history = db_manager.get_chat_messages(state["current_chat_id"])
        formatted_history = [{"role": m[0], "content": m[1]} for m in (raw_history[-5:] if len(raw_history) > 5 else raw_history)]
        chat_box.controls.append(ft.Text(f"You: {txt}", size=12, selectable=True))
        user_input.value = ""
        ai_res_container = ft.Text(f"{ai_params['name']}: ...", color="blue", size=12, selectable=True)         
        chat_box.controls.append(ai_res_container)
        page.update()
        full_bot_response = ""
        try:
            loop = asyncio.get_running_loop()
            gen = ai_brain.get_ai_response_stream(formatted_history, ai_params)
            while True:
                if state["stop_signal"]: break
                chunk = await loop.run_in_executor(None, next, gen, None)
                if chunk is None: break
                full_bot_response += chunk
            if full_bot_response:
                await typewriter_add(ai_res_container, full_bot_response)
        except Exception as ex:
            print(f"Error: {ex}")
        finally:
            if full_bot_response:
                db_manager.save_message(state["current_chat_id"], "assistant", full_bot_response)
            page.update()

    # --- VIEWS ---
    discussion_view = ft.Container(
        content=ft.Column([
            chat_box, 
            ft.Row([
                user_input, 
                ft.Row([
                ft.TextButton(content=ft.Text("+", size=32, color="white", weight="bold"), on_click=forget_context),                      
                ft.TextButton(content=ft.Text("➤", size=26, color="white"), on_click=send_msg)
                ], spacing=0)
            ], vertical_alignment="end")
        ]), padding=10, expand=True
    )

    history_view = ft.Container(
        content=ft.Column([
            ft.Text("Manage Conversations", size=18, weight="bold", color="blue"),
            ft.Row([
                ft.TextButton("Select All", on_click=lambda _: [selected_chats.add(c[0]) for c in db_manager.get_user_chats(state["current_user"])] or refresh_history_view()),
                ft.ElevatedButton("Delete Selected", bgcolor="blue", color="white", on_click=delete_selected),
                ft.TextButton("Wipe All", icon=ft.Icons.DELETE, icon_color="blue", on_click=delete_all),
            ]),
            ft.Divider(height=10, color="white24"),
            history_list
        ]), padding=20, visible=False, expand=True
    )

    # --- SETTINGS ---
    name_f = ft.TextField(label="Name", value=ai_params["name"], height=38, text_size=12, width=220)
    gender_s = ft.Switch(label="Male / Female", value=ai_params["is_male"], scale=0.7)
    persona_f = ft.TextField(label="Persona", value=ai_params["persona"], height=38, text_size=12, expand=True)
    def section_title(text): return ft.Container(content=ft.Text(text, size=10, weight="bold", color="blue"), padding={"left": 5, "top": 5})
    
    creative_s = ft.Slider(min=0, max=200, value=ai_params["creativity"], label="{value}", divisions=200, height=25)
    length_s = ft.Slider(min=16, max=2048, value=ai_params["length"], label="{value}", divisions=127, height=25)
    focus_s = ft.Slider(min=0, max=100, value=ai_params["focus"], label="{value}", divisions=100, height=30)
    variety_s = ft.Slider(min=1, max=200, value=ai_params["variety"], label="{value}", divisions=200, height=30)
    repeat_s = ft.Slider(min=100, max=200, value=ai_params["repetition"], label="{value}", divisions=100, height=30)

    def apply_config(e):
        ai_params.update({"name": name_f.value, "persona": persona_f.value, "is_male": gender_s.value, "creativity": int(creative_s.value), "length": int(length_s.value), "focus": int(focus_s.value), "variety": int(variety_s.value), "repetition": int(repeat_s.value)})
        page.update()

    parameters_view = ft.Container(
        content=ft.Column([
            ft.Container(content=ft.Column([ft.Row([name_f, gender_s], alignment="spaceBetween"), persona_f], spacing=10), padding={"top": 15}),
            section_title("Creativity"), creative_s, 
            section_title("Answer Length"), length_s, 
            section_title("Focus"), focus_s, 
            section_title("Vocabulary Variety"), variety_s, 
            section_title("Repetition Blocker"), repeat_s, 
            ft.Button("SAVE SETTINGS", on_click=apply_config, height=30)
        ], spacing=0), 
        padding={"top": 35, "right": 15, "left": 5}, 
        visible=False, expand=True
    )

   # --- ENCYCLOPEDIA GUIDE (ENHANCED) ---
    guide_content = [
        ft.Text("The Complete Prompting Encyclopedia", size=28, weight="bold", color="blue"),
        ft.Text("Mastering LLM Logic and Creative Control", size=12, italic=True, color="grey"),
        ft.Divider(height=20, color="white24"),
        
        # 1. Zero-Shot
        ft.Text("1. Zero-Shot Prompting", size=20, weight="bold", color="blue"),
        ft.Text("Description: Asking the AI to perform a task without giving any prior examples. This relies entirely on the model's pre-trained knowledge.", size=12, color="white70"),
        ft.Markdown("""**Examples:**\n1. Translate 'Hello' to French.\n2. Write a poem about a cat.\n3. Define quantum physics."""),
        ft.Divider(height=10, color="transparent"),

        # 2. Few-Shot
        ft.Text("2. Few-Shot Prompting", size=20, weight="bold", color="blue"),
        ft.Text("Description: Providing a few examples (shots) of the input-output format you want. This 'teaches' the AI the pattern before it answers.", size=12, color="white70"),
        ft.Markdown("""**Examples:**\n1. Input: Big -> Output: Small. Input: Fast -> Output: Slow. Input: High -> Output: ?\n2. Apple: Fruit, Carrot: Vegetable, Salmon: ?\n3. Happy: 😊, Sad: 😢, Angry: ?"""),
        ft.Divider(height=10, color="transparent"),

        # 3. Chain-of-Thought (CoT)
        ft.Text("3. Chain-of-Thought (CoT)", size=20, weight="bold", color="blue"),
        ft.Text("Description: Forcing the AI to 'think out loud' by breaking down complex logic into step-by-step reasoning. Great for math and troubleshooting.", size=12, color="white70"),
        ft.Markdown("""**Examples:**\n1. Explain step-by-step how to boil an egg.\n2. Solve 25 * 4 + 10 by showing each calculation.\n3. Think aloud: How would you fix a leaky faucet?"""),
        ft.Divider(height=10, color="transparent"),

        # 4. Role & Persona
        ft.Text("4. Role & Persona Prompting", size=20, weight="bold", color="blue"),
        ft.Text("Description: Assigning a specific character or professional identity to the AI. This changes the tone, vocabulary, and expertise level of the response.", size=12, color="white70"),
        ft.Markdown("""**Examples:**\n1. Act as a chef and suggest a dinner recipe.\n2. Respond as a fitness coach for a 5k run.\n3. Speak like a 1920s detective investigating a case."""),
        ft.Divider(height=10, color="transparent"),

        # 5. Tree-of-Thought (ToT)
        ft.Text("5. Tree-of-Thought (ToT)", size=20, weight="bold", color="blue"),
        ft.Text("Description: A strategy where the AI explores multiple different solutions or 'branches' of thought, compares them, and selects the most logical path.", size=12, color="white70"),
        ft.Markdown("""**Examples:**\n1. Give 3 ways to save money and pick the best one.\n2. List 3 vacation spots, compare them, and choose one.\n3. Propose 3 business ideas and evaluate their risks."""),
        
        ft.Container(height=50) 
    ]
    tutorial_view = ft.Container(content=ft.ListView(controls=guide_content, expand=True, spacing=10, padding=30), visible=False, expand=True)
    # --- ABOUT & CREDITS SECTION ---
    about_content = [
        ft.Text("About ZerBo6", size=28, weight="bold", color="blue"),
        ft.Text("Official Release v1.0", size=12, italic=True, color="grey"),
        ft.Divider(height=20, color="white24"),
        
        ft.Text("Creator & Lead Developer", size=16, weight="bold", color="white"),
        ft.Text("Elwardi Zerdazi", size=14, color="blue"),
        ft.Text("This software is an original work focusing on the intersection of AI literacy and human-centric interaction.", size=12),
        
        ft.Divider(height=10, color="transparent"),
        
        ft.Text("Mission & Purpose", size=16, weight="bold", color="white"),
        ft.Markdown("""
        *   **Original Architecture:** Built from the ground up using custom state-management and ASCII animation logic.
        *   **Non-Derivative:** This is a unique standalone application, not a wrapper or copy of existing software.
        """),
        
        ft.Divider(height=10, color="transparent"),

        ft.Text("Open Source Credentials & Tech Stack", size=16, weight="bold", color="white"),
        ft.Text("In the spirit of professional software transparency, this project acknowledges the following open-source technologies:", size=12, color="grey"),
        ft.Markdown("""
        *   **Flet (Flutter for Python):** Powering the multi-platform UI and material design.
        *   **Python 3.x:** The core engine and logic processing language.
        *   **Pillow (PIL):** Used for advanced image processing and grayscale conversion.
        *   **SQLite:** Managing local, secure, and private chat history.
        *   **OpenAI/Groq API:** Driving the 'AI Brain' through professional LLM integration.
        """),

        ft.Divider(height=10, color="transparent"),
        ft.Text("© 2026 Elwardi Zerdazi. All Rights Reserved.", size=10, text_align="center", color="grey"),
        ft.Container(height=50)
    ]

    about_view = ft.Container(content=ft.ListView(controls=about_content, expand=True, spacing=10, padding=30), visible=False, expand=True)
  
    def switch_v(target):
        discussion_view.visible = (target == "chat"); parameters_view.visible = (target == "config"); tutorial_view.visible = (target == "guide"); history_view.visible = (target == "history") ;about_view.visible = (target == "about")
        if target == "history": refresh_history_view()
        page.update()

    def launch_app(username):
        state["current_user"] = username
        state["running"] = True 
        state["current_chat_id"] = None
        chat_box.controls.clear()
        page.clean()
        def nav_icon(s, t, tip): return ft.TextButton(content=ft.Text(s, size=28, color="white", font_family="Segoe UI Symbol"), on_click=lambda _: switch_v(t), tooltip=tip)
        view_toggle = ft.Row([
            nav_icon("💬", "chat", "Chat"), nav_icon("📜", "history", "History"), 
            nav_icon("👤", "config", "Settings"), nav_icon("❓", "guide", "Guide"), nav_icon("ℹ️", "about", "About"),
            ft.TextButton(content=ft.Text("🚪", size=28, color="white", font_family="Segoe UI Symbol"), on_click=logout, tooltip="Logout")
        ], spacing=15)
        
        # Header with branding and "Created by ElWardi" on the far right
        header_row = ft.Row(
            [
                ft.Row(
                    [
                        ft.Image(
                            src=get_path("assets\\logo2.png"),
                            height=35,
                            fit="contain"
                        ),
                        ft.Container(view_toggle, padding={"left": 30})
                    ]
                ),
            ],
            alignment="spaceBetween"
        )

        ascii_display = ft.Text(value="", font_family="Consolas", size=6, color="green", no_wrap=True)
        page.add(ft.Column([ft.Container(header_row, padding={"left": 15, "top": 5}), ft.Row([ft.Column([discussion_view, parameters_view, tutorial_view, history_view,about_view], expand=7), ft.Container(content=ascii_display, expand=5)], expand=True)], expand=True, spacing=0))

        async def animate():
            while state["running"]:
                try:
                    logic = char_logic if ai_params["is_male"] else char_female
                    img = img_male if ai_params["is_male"] else img_female
                    ascii_display.value = logic.get_frame(img, state["is_talking"], time.time() - state["last_action_time"])
                    page.update()
                except: break
                await asyncio.sleep(0.05)
        page.run_task(animate)

    page.add(auth_ui.show_auth_screen(page, launch_app))

if __name__ == "__main__":
    ft.app(main)
