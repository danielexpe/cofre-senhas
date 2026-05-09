"""
Cofre de Senhas - Aplicação Desktop
Autor: Daniel
"""
import customtkinter as ctk
from ui.tela_inicial import TelaInicial


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("🔐 Cofre de Senhas")
    app.geometry("900x600")
    app.minsize(800, 500)

    # Suporte alta DPI no Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    TelaInicial(app)
    app.mainloop()


if __name__ == "__main__":
    main()

