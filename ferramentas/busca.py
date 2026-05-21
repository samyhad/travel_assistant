"""
busca.py — Ferramenta search_by_profile

A ferramenta mais importante da versão evolutiva.
Em vez de o usuário dizer "me fale sobre Lisboa", o agente pergunta:
"dado esse perfil, quais destinos se encaixam?"

O banco de destinos é mockado aqui para focar no comportamento do agente.
Em produção, substitua por uma chamada a uma API de viagens (Amadeus, Skyscanner, etc.)
"""

from langchain_core.tools import tool
from memoria import listar_visitados


# -----------------------------------------------------------------------------
# Base de destinos (mock)
# Cada destino tem atributos comparáveis — isso é o que permite rankeamento.
# -----------------------------------------------------------------------------

DESTINOS = [
    {
        "nome": "Algarve, Portugal",
        "tipo": ["praia", "natureza"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 22,
        "budget": "médio",
        "agitacao": "tranquilo",
        "cultura": "média",
        "seguranca": "alta",
        "tags": ["praia", "falésia", "surf", "gastronomia", "sol"],
    },
    {
        "nome": "Grécia (Santorini)",
        "tipo": ["praia", "cultura", "romântico"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 23,
        "budget": "alto",
        "agitacao": "moderado",
        "cultura": "alta",
        "seguranca": "alta",
        "tags": ["praia", "pôr do sol", "arquitetura", "vinho", "ilhas"],
    },
    {
        "nome": "Croácia (Dubrovnik)",
        "tipo": ["praia", "cultura", "história"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 20,
        "budget": "médio",
        "agitacao": "moderado",
        "cultura": "alta",
        "seguranca": "alta",
        "tags": ["praia", "muralhas", "Game of Thrones", "mar azul"],
    },
    {
        "nome": "Marrocos (Essaouira)",
        "tipo": ["cultura", "praia", "aventura"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 24,
        "budget": "baixo",
        "agitacao": "moderado",
        "cultura": "muito alta",
        "seguranca": "média",
        "tags": ["praia", "medina", "vento", "surf", "mercados", "diferente"],
    },
    {
        "nome": "Tailândia (Koh Lanta)",
        "tipo": ["praia", "natureza", "aventura"],
        "clima_outubro": "quente",
        "temperatura_outubro": 30,
        "budget": "baixo",
        "agitacao": "tranquilo",
        "cultura": "alta",
        "seguranca": "média",
        "tags": ["praia", "tropical", "templos", "comida", "mergulho"],
    },
    {
        "nome": "Madeira, Portugal",
        "tipo": ["natureza", "hiking", "descanso"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 23,
        "budget": "médio",
        "agitacao": "tranquilo",
        "cultura": "média",
        "seguranca": "alta",
        "tags": ["natureza", "levadas", "flores", "montanha", "oceano"],
    },
    {
        "nome": "Espanha (San Sebastián)",
        "tipo": ["gastronomia", "cultura", "praia"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 18,
        "budget": "médio",
        "agitacao": "moderado",
        "cultura": "alta",
        "seguranca": "alta",
        "tags": ["pintxos", "gastronomia", "praia urbana", "cultura basca"],
    },
    {
        "nome": "Ilhas Canárias (La Gomera)",
        "tipo": ["natureza", "hiking", "praia"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 25,
        "budget": "médio",
        "agitacao": "tranquilo",
        "cultura": "média",
        "seguranca": "alta",
        "tags": ["natureza", "floresta", "praia", "trilhas", "silêncio"],
    },
    {
        "nome": "Montenegro (Kotor)",
        "tipo": ["cultura", "natureza", "praia"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 20,
        "budget": "baixo",
        "agitacao": "tranquilo",
        "cultura": "alta",
        "seguranca": "alta",
        "tags": ["fjord", "muralhas", "praia", "Balcãs", "autêntico"],
    },
    {
        "nome": "México (Oaxaca)",
        "tipo": ["cultura", "gastronomia", "aventura"],
        "clima_outubro": "ameno",
        "temperatura_outubro": 25,
        "budget": "baixo",
        "agitacao": "moderado",
        "cultura": "muito alta",
        "seguranca": "média",
        "tags": ["gastronomia", "arte", "mercados", "mezcal", "ruínas"],
    },
]


# -----------------------------------------------------------------------------
# Ferramenta
# -----------------------------------------------------------------------------

@tool
def search_by_profile(criterios: str) -> str:
    """
    Busca destinos turísticos compatíveis com o perfil e critérios do usuário.

    Use esta ferramenta para ENCONTRAR destinos quando o usuário ainda não sabe
    para onde ir. Esta é a ferramenta principal para sugestões personalizadas.

    Entrada esperada: string com critérios separados por vírgula.
    Exemplos:
      "praia, outubro, budget médio, clima ameno"
      "cultura, aventura, budget baixo"
      "tranquilo, natureza, sem praia"

    Retorna: lista dos destinos mais compatíveis com pontuação e justificativa.
    """
    criterios_lower = criterios.lower()
    visitados = [v.lower() for v in listar_visitados()]

    # Pontuação de cada destino contra os critérios
    resultados = []

    for d in DESTINOS:
        # Pula destinos já visitados
        if any(v in d["nome"].lower() for v in visitados):
            continue

        score = 0
        motivos = []

        # Tipo de viagem
        for tipo in d["tipo"]:
            if tipo in criterios_lower:
                score += 3
                motivos.append(tipo)

        # Budget
        for nivel in ["baixo", "médio", "alto"]:
            if nivel in criterios_lower and nivel == d["budget"]:
                score += 2
                motivos.append(f"budget {nivel}")

        # Clima / temperatura
        if "ameno" in criterios_lower and d["clima_outubro"] == "ameno":
            score += 2
            motivos.append("clima ameno em outubro")
        if "quente" in criterios_lower and d["clima_outubro"] == "quente":
            score += 2
            motivos.append("clima quente")

        # Perfil de agitação
        if "tranquilo" in criterios_lower and d["agitacao"] == "tranquilo":
            score += 2
            motivos.append("destino tranquilo")
        if "agitado" in criterios_lower and d["agitacao"] in ["moderado", "agitado"]:
            score += 1

        # Tags livres
        for tag in d["tags"]:
            if tag in criterios_lower:
                score += 1
                motivos.append(tag)

        # Segurança sempre conta positivamente
        if d["seguranca"] == "alta":
            score += 1

        resultados.append({
            "destino": d["nome"],
            "score": score,
            "motivos": list(set(motivos)),
            "budget": d["budget"],
            "temperatura": f"{d['temperatura_outubro']}°C em outubro",
        })

    # Ordena por score e retorna top 5
    resultados.sort(key=lambda x: x["score"], reverse=True)
    top = resultados[:5]

    if not top:
        return "Nenhum destino encontrado para esses critérios. Tente ampliar os filtros."

    linhas = ["Destinos mais compatíveis com o perfil:\n"]
    for i, r in enumerate(top, 1):
        motivos_str = ", ".join(r["motivos"]) if r["motivos"] else "compatibilidade geral"
        linhas.append(
            f"{i}. {r['destino']} — score {r['score']} | "
            f"budget {r['budget']} | {r['temperatura']} | "
            f"pontos fortes: {motivos_str}"
        )

    return "\n".join(linhas)