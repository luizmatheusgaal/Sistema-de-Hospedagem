import customtkinter as ctk
import os
from dotenv import load_dotenv

load_dotenv()


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success

        login_title = ctk.CTkLabel(
            self,
            text="Sistema de Gestão da Pousada",
            font=("Arial", 28, "bold"),
        )
        login_title.pack(pady=(80, 20))

        subtitle = ctk.CTkLabel(
            self, text="🏨 Acesso Administrativo",
            font=("Arial", 20)
            )
        subtitle.pack(pady=(0,20))

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.password_entry.pack(pady=10)

        login_button = ctk.CTkButton(self, text="Entrar", height = 40, corner_radius=10, command=self.validate_login)
        login_button.pack(pady=10)

        self.login_feedback_label = ctk.CTkLabel(self, text="")
        self.login_feedback_label.pack(pady=5)

        self.master.bind("<Return>", self.validate_login)

    def validate_login(self, event=None):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if username == os.getenv("USUARIO_LOGIN") and password == os.getenv("SENHA_LOGIN"):
            self.login_feedback_label.configure(
                text="Login realizado com sucesso", text_color="green"
            )
            self.master.unbind("<Return>")
            self.destroy()
            self.on_login_success()
        else:
            self.login_feedback_label.configure(text="Login incorreto", text_color="red")
