# Sistema de Hospedagem (Pousada)

Aplicação desktop em **Python + CustomTkinter** para gestão de pousada, com cadastro de quartos, check-in/check-out, consumos (insumos), tipos de quarto e histórico com exportação.

## Funcionalidades
- Login do administrador.
- Cadastro/edição de quartos.
- Cadastro/edição de tipos de quarto.
- Cadastro/edição de insumos (consumos).
- Check-in, consumo e check-out.
- Histórico por data com filtros e exportação CSV.
- Relatório de fechamento salvo em arquivo.

## Requisitos
- Python 3.9+
- MySQL (com usuário e banco configurados)

## Instalação
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração (.env)
Crie um arquivo `.env` na raiz do projeto:
```env
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=pousada
DB_PORT=3306

LIMITE_QUARTOS=10
VALOR_DIARIA=150.00
USUARIO_LOGIN=admin
SENHA_LOGIN=123trivago
```

## Executar
```bash
python .\src\login.py
```

## Relatórios
Ao encerrar o expediente, o sistema pergunta onde salvar o relatório. Por padrão, ele sugere a pasta `src\report`.

## Estrutura de Pastas
```
Sistema-de-Hospedagem/
├─ src/
│  ├─ login.py
│  ├─ service.py
│  ├─ db.py
│  ├─ interface/
│  │  ├─ ui_main.py
│  │  ├─ ui_login.py
│  │  └─ ...
│  └─ report/
├─ .env
└─ README.md
```

## Observações
- As tabelas são criadas automaticamente se não existirem.
- O banco **não** é resetado ao iniciar o sistema.
