# 🔍 Workana Freelance Crawler

API desenvolvida para buscar e extrair informações de freelancers do site Workana, filtrando por categorias e subcategorias específicas.

## 📋 Sobre o Projeto

Este projeto foi desenvolvido para funcionar em conjunto com um AI Agent criado no n8n. Através de linguagem natural, o agente conversa com o usuário para identificar os tópicos de freelance desejados, formata a requisição e envia para esta API.

O sistema consulta o Workana e retorna dados estruturados sobre projetos freelance disponíveis, incluindo:
- Título e descrição do projeto
- Informações do cliente
- Orçamento e tipo de pagamento
- Localização
- Habilidades requeridas
- Quantidade de propostas
- PDF com relatório formatado

## 🚀 Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido para construção de APIs
- **Requests** - Para realizar requisições HTTP ao Workana
- **ReportLab** - Geração de PDFs com os resultados
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

## 📦 Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd crawler_freelance
```

2. Crie um ambiente virtual:
```bash
python -m venv env
```

3. Ative o ambiente virtual:
```bash
# Windows
.\env\Scripts\activate

# Linux/Mac
source env/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:
   - Copie o arquivo `.env.example` para `.env`
   - Edite o arquivo `.env` e configure sua chave de API

```bash
cp .env.example .env
```

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto com a seguinte variável:

```env
API_KEY=sua_chave_de_api_aqui
```

## 🎯 Como Usar

1. Inicie o servidor:
```bash
uvicorn main:app --reload
```

2. A API estará disponível em `http://localhost:8000`

3. Acesse a documentação interativa em `http://localhost:8000/docs`

## 📡 Endpoints

### GET `/freelance/`

Busca freelancers no Workana por categoria e subcategoria.

**Headers:**
- `Authorization: Bearer {API_KEY}`

**Query Parameters:**
- `category` (opcional): Categoria do freelance
- `subcategory` (opcional): Subcategoria específica

**Exemplo de Request:**
```bash
curl -X GET "http://localhost:8000/freelance/?category=it-programming&subcategory=web-development" \
  -H "Authorization: Bearer sua_api_key"
```

**Resposta:**
```json
{
  "status": true,
  "freelances": [
    {
      "id": "exemplo-projeto",
      "titulo": "EXEMPLO PROJETO",
      "url": "https://www.workana.com/job/exemplo-projeto",
      "nome_cliente": "João Silva",
      "localizacao": "Brasil",
      "orcamento": {
        "moeda": "USD",
        "min": 100,
        "max": 500
      },
      "pagamento_por_hora": false,
      "postado_em": "2025-12-18",
      "qtd_propostas": "5",
      "habilidades": ["Python", "FastAPI"],
      "descricao": "Descrição do projeto..."
    }
  ],
  "pdf": "base64_encoded_pdf..."
}
```

### GET `/freelance/categories`

Retorna todas as categorias e subcategorias disponíveis.

**Headers:**
- `Authorization: Bearer {API_KEY}`

**Exemplo de Request:**
```bash
curl -X GET "http://localhost:8000/freelance/categories" \
  -H "Authorization: Bearer sua_api_key"
```

## 🗂️ Categorias Disponíveis

- **it-programming**: Programação e TI
  - web-development, mobile-development, wordpress, e-commerce, data-science, etc.
  
- **design-multimedia**: Design e Multimídia
  - logo-design, web-design, illustrations, 3d-models, etc.
  
- **writing-translation**: Redação e Tradução
  - article-writing, translation, proofreading, etc.
  
- **sales-marketing**: Vendas e Marketing
  - seo, community-management, e-mail-marketing, etc.
  
- **admin-support**: Suporte Administrativo
  - virtual-assistant, customer-support, data-entry, etc.
  
- **legal**: Jurídico
  
- **finance-management**: Finanças e Gestão
  - accounting, project-management, recruiting, etc.
  
- **engineering-manufacturing**: Engenharia e Manufatura
  - industrial-design, cad-drawing, 3d-modelling, etc.

## 🔐 Autenticação

Todas as requisições devem incluir o header `Authorization` com o Bearer token:

```
Authorization: Bearer {API_KEY}
```

## 📄 Geração de PDF

O projeto possui uma função `generate_pdf()` completamente funcional que gera relatórios em PDF dos freelancers encontrados. 

**Situação atual:** A função já está implementada e retorna o PDF em formato base64 no campo `pdf` da resposta do endpoint `/freelance/`.

**Personalização:** Caso deseje modificar o comportamento (como não gerar PDF por padrão ou criar um endpoint separado), a função está pronta em [controllers/freelance_controller.py](controllers/freelance_controller.py) e pode ser facilmente adaptada às suas necessidades.

## 🏗️ Estrutura do Projeto

```
crawler_freelance/
├── main.py                          # Ponto de entrada da aplicação
├── requirements.txt                 # Dependências do projeto
├── .env                             # Variáveis de ambiente (não versionado)
├── .env.example                     # Exemplo de variáveis de ambiente
└── controllers/
    ├── __init__.py
    └── freelance_controller.py      # Lógica de negócio e rotas
```

## 🤝 Integração com n8n

Este projeto foi projetado para funcionar com um AI Agent no n8n. O fluxo típico é:

1. Usuário conversa em linguagem natural com o AI Agent
2. Agent identifica categoria/subcategoria desejada
3. Agent formata a requisição HTTP para esta API
4. API retorna dados estruturados + PDF
5. Agent processa e apresenta os resultados ao usuário

## 📝 Licença

Este projeto é de uso livre.

## 👨‍💻 Autor

Desenvolvido para integração com AI Agents
