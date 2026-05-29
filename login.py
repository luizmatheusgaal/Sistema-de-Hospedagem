import customtkinter as ctk
ctk.set_appearance_mode('light')#defini cor do fundo
app=ctk.CTk()#cria janela principal
app.title('Login no sistema')
app.geometry('700x600')

#funções
def validar():
    user = usuario.get()
    password = senha.get()
    if user=='admin' and password=='123trivago':
        positivo.configure(text="Login realizado com sucesso", text_color='green')
    else:
        positivo.configure(text="Login incorreto", text_color='red')

#body do sistema
usuario_label=ctk.CTkLabel(app,text='Usuário', text_color='black')
usuario_label.pack(pady=15)#adiciona a variavel ao sistema, pady gera espaço entre elementos

usuario=ctk.CTkEntry(app,placeholder_text='Insira seu usuário')
usuario.pack(pady=5)

senha_label=ctk.CTkLabel(app,text='Senha', text_color='black')
senha_label.pack(pady=15)#adiciona a variavel ao sistema, pady gera espaço entre elementos

senha=ctk.CTkEntry(app,placeholder_text='Digite sua senha', show='*')
senha.pack(pady=5)

#login
botao=ctk.CTkButton(app,text='Entrar', command=validar)
botao.pack(pady=10)

#retorno de login
positivo=ctk.CTkLabel(app,text='')
positivo.pack(pady=3)

#inicia o sistema
app.mainloop()