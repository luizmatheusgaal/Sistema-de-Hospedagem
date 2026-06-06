from tkinter import messagebox

import customtkinter as ctk

from service import LodgingService
from interface.ui_login import LoginScreen


def main():
    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("Sistema de Pousada")
    app.update_idletasks()
    app.after(0, lambda: app.state("zoomed"))

    def show_login():
        login_screen = LoginScreen(app, open_main_screen)
        login_screen.pack(fill="both", expand=True)

    def open_main_screen():
        pass

    show_login()

    app.mainloop()


if __name__ == "__main__":
    main()
