import requests, json, re
from html import unescape
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

def json_to_file(data: json):
    with open('resposta.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def format_title(title: str):
    newTitle = title.replace('-', ' ')
    return newTitle.upper()

def format_country(country: str):
    index1 = country.find('title=\"')
    index2 = country.find("\" loading=", index1)
    return country[index1+7:index2]

def format_budget(budget: str):
    currency_match = re.match(r"([A-Z]{3})", budget.strip())
    currency = currency_match.group(1) if currency_match else None

    numbers = re.findall(r"[\d\.]+", budget)
    values = [int(num.replace(".", "")) for num in numbers]

    if len(values) == 2:
        min_val, max_val = values
    elif len(values) == 1:
        min_val, max_val = values[0], values[0]
    else:
        min_val = max_val = None

    return {
        "currency": currency,
        "min": min_val,
        "max": max_val
    }

def format_bids(bids: str):
    return bids.replace('Propostas: ', '')

def format_skills(skills: list):
    ret = []
    for skill in skills:
        ret.append(skill['anchorText'])
    return ret

def format_description(description: str):
    limite = 200 # qtd max de caracteres
    texto = re.sub(r"<[^>]+>", "", description)
    texto = unescape(texto).strip()
    primeiro_ponto = texto.find(".")
    if 0 < primeiro_ponto <= limite:
        return texto[:primeiro_ponto+1]
    return (texto[:limite] + "...") if len(texto) > limite else texto

KEY = "sk_live_7d8f2e1a0b934c3c9f67a4b2d8d5f11e"

router = APIRouter(prefix="/freelance", tags=["freelance"])
@router.get('/', status_code=status.HTTP_200_OK)
def get_freelance(request: Request):
    auth = request.headers.get('Authorization')
    if auth != f'Bearer {KEY}':
        raise HTTPException(status_code=401, detail="Unauthorized")

    URL = "https://www.workana.com/jobs?category=it-programming&language=pt&subcategory=web-development"

    HEADERS = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/127.0.0.0 Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": URL,
    }

    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    if(resp.status_code == 200):
        data = resp.json()
        resultados = data['results']['results']

        response = []

        for resultado in resultados:
            resp_resultado = {}
            resp_resultado['id'] = resultado['slug']
            resp_resultado['titulo'] = format_title(resultado['slug'])
            resp_resultado['url'] = f'https://www.workana.com/job/{resultado['slug']}'
            resp_resultado['nome_cliente'] = resultado['authorName']
            resp_resultado['localizacao'] = format_country(resultado['country'])
            resp_resultado['orcamento'] = format_budget(resultado['budget'])
            resp_resultado['pagamento_por_hora'] = resultado['isHourly']
            resp_resultado['postado_em'] = resultado['postedDate']
            resp_resultado['qtd_propostas'] = format_bids(resultado['totalBids'])
            resp_resultado['habilidades'] = format_skills(resultado['skills'])
            resp_resultado['descricao'] = format_description(resultado['description'])
            
            response.append(resp_resultado)
        return JSONResponse(content={'status': True, 'freelances': response})
    else:   
        raise HTTPException(status_code=500, detail='Erro ao realizar a requisição')


# {
#   "id": "desenvolvedor-front-end-para-dashboard-de-analytics-de-videos",
#   "title": "Desenvolvedor Front-End para Dashboard de Analytics de Vídeos",
#   "url": "https://www.workana.com/job/desenvolvedor-front-end-para-dashboard-de-analytics-de-videos",
#   "client_name": "P. H.",
#   "location": "Brasil",
#   "budget": { "currency": "USD", "min": 1000, "max": 3000 },
#   "is_hourly": false,
#   "posted_at": "2025-09-10T??:??:00-03:00",
#   "proposals_count": 22,
#   "skills": ["HTML","CSS","JavaScript","Responsive Web Design","Aptidão de programação"],
#   "short_description": "Buscamos dev front-end para replicar um dashboard de analytics de vídeos, com gráficos interativos, filtros por período, layout responsivo e exportação básica..."
# }
