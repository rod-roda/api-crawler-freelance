import requests, json, re
from html import unescape
from fastapi import APIRouter, HTTPException, status, Request, Query
from fastapi.responses import JSONResponse
from typing import Optional

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

def call_api(category = 'it-programming', subcategory = 'web-development'):
    URL = f"https://www.workana.com/jobs?category={category}&language=pt{f'&subcategory={subcategory}' if subcategory != None else ''}"

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

        if(len(resultados) == 0): return {'status': False, 'msg': 'Sem freelances disponíveis'}

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
        return {'status': True, 'freelances': response}
    else:   
        return {'status': False, 'msg': 'Erro ao realizar a requisição'}

KEY = "sk_live_7d8f2e1a0b934c3c9f67a4b2d8d5f11e"
CATEGORY_SUBCATEGORY = {
    'it-programming': (
        'web-development',
        'web-design',
        'e-commerce',
        'wordpress-1',
        'mobile-development',
        'data-science-1',
        'desktop-apps',
        'artificial-intelligence-1',
        'others-5'
    ),
    'design-multimedia': (
        'logo-design',
        'web-design-1',
        'banners',
        'illustrations',
        'make-or-edit-a-video',
        'infographics',
        'images-for-social-networks',
        'mobile-app-design',
        'corporate-image',
        '3d-models',
        'landing-page',
        'fashion-design-1',
        'artificial-intelligence-2',
        'others-1'
    ), 
    'writing-translation': (
        'article-writing-1',
        'writing-for-websites',
        'proofreading-1',
        'content-for-social-networks',
        'translation',
        'subtitling-1',
        'artificial-intelligence-7',
        'others-6'
    ), 
    'sales-marketing': (
        'seo',
        'community-management',
        'advertising-on-google-facebook',
        'e-mail-marketing',
        'data-analytics',
        'televentas',
        'sales-executive',
        'artificial-intelligence-6',
        'others'
    ),
    'admin-support': (
        'virtual-assistant-1',
        'customer-support',
        'data-entry-1',
        'market-research-1',
        'telesales',
        'artificial-intelligence-3',
        'others-2'
    ), 
    'legal': (), 
    'finance-management': (
        'gather-data',
        'work-with-a-crm',
        'project-management-1',
        'recruiting',
        'strategic-planning-1',
        'accounting-1',
        'artificial-intelligence-5',
        'others-4'
    ), 
    'engineering-manufacturing': (
        'industrial-design-1',
        'cad-drawing',
        '3d-modelling-1',
        'interior-design-1',
        'artificial-intelligence-4',
        'others-3'
    )
}

router = APIRouter(prefix="/freelance", tags=["freelance"])
@router.get("/", status_code=status.HTTP_200_OK)
def get_freelance(
    request: Request,
    category: Optional[str] = Query(None, description="Categoria (opcional)"),
    subcategory: Optional[str] = Query(None, description="Subcategoria (opcional)")
):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if subcategory == "":
        subcategory = None

    if category and category not in CATEGORY_SUBCATEGORY:
        raise HTTPException(status_code=400, detail="Categoria indisponível")

    if subcategory and not category:
        raise HTTPException(status_code=400, detail="Informe 'category' quando usar 'subcategory'")

    if subcategory and subcategory not in CATEGORY_SUBCATEGORY[category]:
        raise HTTPException(status_code=400, detail="Subcategoria indisponível")

    ret = call_api(category, subcategory) if category else call_api()

    if ret.get("status"):
        return JSONResponse(content={"status": True, "freelances": ret["freelances"]})

    raise HTTPException(status_code=500, detail=ret.get("msg", "Erro interno"))

@router.get('/categories', status_code=status.HTTP_200_OK)
def get_categories(request: Request):
    auth = request.headers.get('Authorization')
    if auth != f'Bearer {KEY}':
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return JSONResponse(content={'status': True, 'categories': CATEGORY_SUBCATEGORY})
