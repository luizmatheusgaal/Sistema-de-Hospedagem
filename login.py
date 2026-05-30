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

#segunda tela
def janela_principal():
    app.withdraw()
    janela_hist=ctk.CTkToplevel()
    janela_hist.title("Histórico de hospedagens")
    janela_hist.geometry('1000x750')
    janela_hist.protocol("WM_DELETE_WINDOW", app.quit)
    janela_hist.configure(fg_color="white")

    def janela_novahosp():
        janela_hist.withdraw()
        janela_hosp=ctk.CTkToplevel()
        janela_hosp.title("Nova Hospedagem")
        janela_hosp.geometry('1000x750')
        janela_hosp.protocol("WM_DELETE_WINDOW", app.quit)
        janela_hosp.configure(fg_color="white")
        barra_hosp=ctk.CTkFrame(
        janela_hist,
        fg_color="#A09E9E",
        height=85,
        )
        barra_hosp=ctk.CTkFrame(
        janela_hosp,
        fg_color="#A09E9E",
        height=85,
        )
        barra_hosp.pack(fill="x", padx=20, pady=20)
        barra_hosp.grid_propagate(False)

        barra_hosp.grid_columnconfigure(0, weight=1, uniform="col")  # Coluna da esquerda
        barra_hosp.grid_columnconfigure(1, weight=0, uniform="col")  # Coluna do meio
        barra_hosp.grid_columnconfigure(2, weight=1, uniform="col")  # Coluna da direita
        barra_hosp.grid_rowconfigure(0, weight=1)
        
        titulo_hotelhosp=ctk.CTkLabel(
        barra_hosp,
        text="Hotel Boa Noite",
        text_color="black",
        font=("Arial", 22, "bold")
        )
        titulo_hotelhosp.grid(row=0, column=0, sticky="w", padx=35)

        nome_janelahosp=ctk.CTkLabel(
        barra_hosp,
        text="Nova Hospedagem",
        text_color="black",
        font=("Arial", 20, "bold")
        )
        nome_janelahosp.place(relx=0.5, rely=0.5, anchor="center")

        def voltar_para_principal():
            janela_hosp.destroy() 
            janela_hist.deiconify()


        botao_novahosp=ctk.CTkButton(
        barra_hosp,
        text="Histórico de \n Hospedagem",
        fg_color="white",
        text_color="black",
        border_width=1,
        border_color="gray",
        hover_color="#e5e5e5",
        corner_radius=20,
        width=150,
        height=45,
        command=voltar_para_principal,
        )
        botao_novahosp.grid(row=0, column=2, sticky="e", padx=20)


    barra=ctk.CTkFrame(
        janela_hist,
        fg_color="#A09E9E",
        height=85,
    )
    barra.pack(fill="x", padx=20, pady=20)
    barra.grid_propagate(False)

    barra.grid_columnconfigure(0, weight=1, uniform="col")  # Coluna da esquerda
    barra.grid_columnconfigure(1, weight=0, uniform="col")  # Coluna do meio
    barra.grid_columnconfigure(2, weight=1, uniform="col")  # Coluna da direita
    barra.grid_rowconfigure(0, weight=1)

    titulo_hotel=ctk.CTkLabel(
        barra,
        text="Hotel Boa Noite",
        text_color="black",
        font=("Arial", 22, "bold")
    )
    titulo_hotel.grid(row=0, column=0, sticky="w", padx=35)

    nome_janela=ctk.CTkLabel(
        barra,
        text="Histórico de Hospedagens",
        text_color="black",
        font=("Arial", 20, "bold")
    )
    nome_janela.place(relx=0.5, rely=0.5, anchor="center")

    botao_novahosp=ctk.CTkButton(
        barra,
        text="Nova \n Hospedagem",
        fg_color="white",
        text_color="black",
        border_width=1,
        border_color="gray",
        hover_color="#e5e5e5",
        corner_radius=20,
        width=150,
        height=45,
        command=janela_novahosp,
    )
    botao_novahosp.grid(row=0, column=2, sticky="e", padx=20)

#funções
def validar():
    user = usuario.get()
    password = senha.get()
    if user=='admin' and password=='123trivago':
        positivo.configure(text="Login realizado com sucesso", text_color='green')
        janela_principal()
    else:
        positivo.configure(text="Login incorreto", text_color='red')

#login
botao=ctk.CTkButton(app,text='Entrar', command=validar)
botao.pack(pady=10)

#retorno de login
positivo=ctk.CTkLabel(app,text='')
positivo.pack(pady=3)


#inicia o sistema
app.mainloop()