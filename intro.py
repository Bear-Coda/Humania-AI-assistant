import flet as ft
import asyncio
import os
import sys

def get_path(rel_path):
    """Get the absolute path to the resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

async def show_intro(page: ft.Page):
    # Do NOT set window size here; let main handle the frame.
    # Just set the background and center the logo.
    page.bgcolor = "black"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    logo = ft.Image(
        src=get_path("assets\\logo.png"),
        width=200,
        height=200,
        opacity=1.0,
        animate_opacity=500, 
    )

    page.add(logo)

    # 3-second blinking loop
    for _ in range(3): 
        logo.opacity = 0.1
        page.update()
        await asyncio.sleep(0.5)
        logo.opacity = 1.0
        page.update()
        await asyncio.sleep(0.5)

    # Clear and reset for the chat UI
    page.controls.clear()
    page.bgcolor = None  
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.update()