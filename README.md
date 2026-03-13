# API Empreendimentos SC

API REST para gerenciamento de empreendimentos no estado de Santa Catarina, desenvolvida como desafio prático do programa SENAI/SC LAB365 "IA para DEVs".

## Descrição

Este projeto implementa um backend completo com operações CRUD (Create, Read, Update, Delete) para cadastro e gerenciamento de empreendimentos catarinenses. A API valida municípios contra a lista oficial dos 295 municípios de SC, segmentos de atuação e dados dos empreendedores.

## Stack Tecnológico

- **FastAPI** — Framework web assíncrono com documentação Swagger/OpenAPI automática
- **Supabase** — Backend-as-a-Service com PostgreSQL gerenciado (acessado via REST API/PostgREST)
- **httpx** — Cliente HTTP assíncrono para comunicação com a API REST do Supabase
- **Pydantic v2** — Validação de dados com type hints e validators customizados
- **Uvicorn** — Servidor ASGI de alta performance (desenvolvimento local)
- **Vercel** — Deploy serverless em produção
- **Python 3.9+**

## Estrutura do Projeto

```
├── README.md
├── requirements.txt
├── vercel.json               # Configuração do deploy Vercel
├── .env.example
├── create_table.sql
├── api/
│   └── index.py              # Entrypoint Vercel (self-contained)
├── app/
│   ├── __init__.py
│   ├── main.py               # App FastAPI, CORS, rotas
│   ├── config.py             # Variáveis de ambiente
│   ├── schemas.py            # Modelos Pydantic com validadores
│   ├── crud.py               # Operações CRUD assíncronas com httpx
│   └── supabase_client.py    # Factory de cliente httpx assíncrono
└── tests/
    ├── __init__.py
    ├── conftest.py            # Fixtures e mocks assíncronos
    ├── test_schemas.py        # Testes de validação
    └── test_api.py            # Testes de endpoints
```

## Pré-requisitos

- Python 3.9 ou superior
- Conta no [Supabase](https://supabase.com) com projeto criado
- pip (gerenciador de pacotes Python)

## Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/ernestodeoliveira/desafio_pratico_sctec.git
   cd desafio_pratico_sctec
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados:**
   - Crie um projeto no Supabase
   - Execute o script `create_table.sql` no SQL Editor do dashboard

5. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais do Supabase
   ```

6. **Inicie o servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Acesse a documentação:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Deploy em Produção (Vercel)

A API está disponível em produção via Vercel:

- **API:** https://desafio-pratico-sctec-backend.vercel.app
- **Swagger UI:** https://desafio-pratico-sctec-backend.vercel.app/docs

O deploy utiliza o arquivo `api/index.py` como entrypoint serverless, que contém toda a aplicação em um único arquivo para compatibilidade com o runtime Python da Vercel.

## Endpoints da API

| Método | Rota | Descrição | Status |
|--------|------|-----------|--------|
| POST | `/empreendimentos/` | Criar empreendimento | 201 |
| GET | `/empreendimentos/` | Listar com filtros | 200 |
| GET | `/empreendimentos/{id}` | Buscar por ID | 200 |
| PUT | `/empreendimentos/{id}` | Atualizar | 200 |
| DELETE | `/empreendimentos/{id}` | Remover | 204 |

### Filtros disponíveis (GET /empreendimentos/)

- `?municipio=Florianópolis`
- `?segmento=Tecnologia`
- `?status=ativo`
- `?limit=10&offset=0`

## Exemplos de Uso

```bash
# Criar empreendimento
curl -X POST http://localhost:8000/empreendimentos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nome_empreendimento": "Tech Solutions SC",
    "nome_empreendedor": "João Silva",
    "municipio": "Florianópolis",
    "segmento": "Tecnologia",
    "email": "joao@example.com"
  }'

# Listar com filtro
curl http://localhost:8000/empreendimentos/?municipio=Florianópolis&segmento=Tecnologia

# Buscar por ID
curl http://localhost:8000/empreendimentos/1

# Atualizar
curl -X PUT http://localhost:8000/empreendimentos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nome_empreendimento": "Tech Solutions SC Updated",
    "nome_empreendedor": "João Silva",
    "municipio": "Blumenau",
    "segmento": "Tecnologia",
    "status": "ativo"
  }'

# Remover
curl -X DELETE http://localhost:8000/empreendimentos/1
```

## Testes

```bash
pytest -v
```

## Vídeo Pitch

[Vídeo demonstração da API](https://www.youtube.com/watch?v=gpK2nnzA4Es)

## Boas Práticas Utilizadas

- Arquitetura modular com separação de responsabilidades
- Validação robusta com Pydantic v2 e validators customizados
- Operações assíncronas com httpx.AsyncClient (não bloqueia o event loop)
- HTTPExceptions com códigos de status corretos
- Documentação Swagger completa com tags e descrições
- CORS habilitado para integração com frontends
- Testes automatizados com mocks assíncronos
- Type hints em todas as funções públicas
- Herança em schemas para eliminar duplicação de código
- Logging estruturado para rastreabilidade
- Variáveis de ambiente para configuração segura
- Context managers para gerenciamento de recursos (httpx clients)
