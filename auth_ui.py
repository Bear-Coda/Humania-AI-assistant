import flet as ft
import db_manager

def show_auth_screen(page: ft.Page, on_login_success):
    db_manager.init_db()
    
    user_f = ft.TextField(label="Username", width=300, border_color="blue")
    pass_f = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True, border_color="blue")
    error_msg = ft.Text("", size=12)

    def handle_login(e):
        # This matches the function in db_manager.py
        if db_manager.validate_user(user_f.value, pass_f.value):
            on_login_success(user_f.value)
        else:
            error_msg.value = "Invalid username or password!"
            error_msg.color = "red"
            page.update()

    def handle_register(e):
        if user_f.value and pass_f.value:
            # This matches the function in db_manager.py
            if db_manager.create_user(user_f.value, pass_f.value):
                error_msg.value = "Account created! You can now login."
                error_msg.color = "green"
            else:
                error_msg.value = "Username already taken!"
                error_msg.color = "red"
        else:
            error_msg.value = "Please fill all fields."
            error_msg.color = "orange"
        page.update()

    return ft.Container(
        content=ft.Column([
            ft.Text("Secure Login", size=30, weight="bold", color="white"),
            user_f, pass_f, error_msg,
            ft.Row([
                ft.ElevatedButton(content=ft.Text("LOGIN", color="white"), on_click=handle_login, bgcolor="blue"),
                ft.TextButton(content=ft.Text("CREATE ACCOUNT", color="white"), on_click=handle_register)
            ], alignment="center")
        ], horizontal_alignment="center", alignment="center"),
        expand=True
    )