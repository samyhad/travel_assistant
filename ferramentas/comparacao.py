"""
comparacao.py — Ferramenta compare_destinations

Compara dois ou mais destinos lado a lado em atributos-chave.
Permite que o agente raciocine sobre trade-offs antes de recomendar.
"""

from langchain.tools import tool
from ferramentas.busca import DESTINOS


def _encontrar_destino(nome: str) -> dict | None:
    """Busca um destino pelo nome (busca parcial, case-insensitive)."""
    nome_lower = nome.lower().strip()
    for d in DESTINOS:
        if nome_lower in d["nome"].lower():
            return d
    return None


@tool
def compare_destinations(destinos: str) -> str:
    """
    Compara dois ou mais destinos turísticos lado a lado.

    Use esta ferramenta quando o agente já tem candidatos e quer avaliar
    trade-offs antes de fazer uma recomendação final.

    Entrada esperada: nomes dos destinos separados por vírgula.
    Exemplos:
      "Algarve, Grécia, Croácia"
      "Madeira, Canárias"

    Retorna: tabela comparativa com clima, budget, agitação, cultura e tags.
    """
    nomes = [n.strip() for n in destinos.split(",")]
    encontrados = []

    for nome in nomes:
        d = _encontrar_destino(nome)
        if d:
            encontrados.append(d)
        else:
            encontrados.append({"nome": nome, "_nao_encontrado": True})

    if not encontrados:
        return "Nenhum dos destinos informados foi encontrado na base."

    linhas = ["Comparação de destinos:\n"]
    atributos = [
        ("Budget", "budget"),
        ("Temperatura (out)", "temperatura_outubro"),
        ("Clima (out)", "clima_outubro"),
        ("Agitação", "agitacao"),
        ("Cultura", "cultura"),
        ("Segurança", "seguranca"),
    ]

    # Cabeçalho
    nomes_col = " | ".join(d.get("nome", "?") for d in encontrados)
    linhas.append(f"{'Atributo':<22} | {nomes_col}")
    linhas.append("-" * (22 + 3 + len(nomes_col)))

    # Linhas de atributos
    for label, chave in atributos:
        valores = []
        for d in encontrados:
            if d.get("_nao_encontrado"):
                valores.append("não encontrado")
            else:
                val = d.get(chave, "—")
                valores.append(str(val) if chave != "temperatura_outubro" else f"{val}°C")
        linhas.append(f"{label:<22} | {' | '.join(valores)}")

    # Tags
    linhas.append("")
    for d in encontrados:
        if not d.get("_nao_encontrado"):
            tags = ", ".join(d.get("tags", []))
            linhas.append(f"{d['nome']} → {tags}")

    return "\n".join(linhas)