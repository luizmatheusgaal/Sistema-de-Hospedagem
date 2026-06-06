from tkinter import messagebox

import customtkinter as ctk

from service import LodgingService
from interface.ui_login import LoginScreen
from interface.ui_main import MainScreen


def main():
    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("Sistema de Pousada")
    app.update_idletasks()
    app.after(0, lambda: app.state("zoomed"))

    service = LodgingService()

    def show_login():
        login_screen = LoginScreen(app, open_main_screen)
        login_screen.pack(fill="both", expand=True)

    def open_main_screen():
        main_screen = MainScreen(app, service, show_login)
        main_screen.pack(fill="both", expand=True)
        app.protocol("WM_DELETE_WINDOW", confirm_exit)

    def confirm_exit():
        if messagebox.askyesno("Sair", "Deseja sair?"):
            app.destroy()

    show_login()

    app.mainloop()


if __name__ == "__main__":
    main()
