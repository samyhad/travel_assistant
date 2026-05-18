"""
historico.py — Ferramentas de controle de destinos visitados

check_visited: verifica se um destino foi visitado
save_visited:  registra que o usuário visitou um destino
list_visited:  lista todos os destinos visitados
"""

from langchain.tools import tool
from memoria import adicionar_visitado, listar_visitados, foi_visitado


@tool
def check_visited(destino: str) -> str:
    """
    Verifica se o usuário já visitou um destino específico.

    Use antes de sugerir um destino, para não recomendar lugares
    que o usuário já conhece (a menos que ele peça explicitamente).

    Entrada: nome do destino — ex: "Lisboa" ou "Tailândia"
    Retorna: confirmação se foi ou não visitado.
    """
    if foi_visitado(destino):
        visitados = listar_visitados()
        # Tenta encontrar detalhes extras (ano, nota)
        from memoria.gerenciador import carregar_perfil
        perfil = carregar_perfil()
        for v in perfil["visitados"]:
            if v["destino"].lower() == destino.lower():
                ano = v.get("ano", "ano não registrado")
                nota = v.get("nota")
                nota_str = f", nota: {nota}/10" if nota else ""
                return f"Sim, {destino} já foi visitado ({ano}{nota_str})."
        return f"Sim, {destino} já está na lista de visitados."
    return f"Não, {destino} ainda não foi visitado. É um candidato válido para sugestão."


@tool
def save_visited(info: str) -> str:
    """
    Registra que o usuário visitou um destino. Chame esta ferramenta sempre
    que o usuário mencionar que já esteve em algum lugar.

    Entrada esperada: "destino, ano, nota" — ano e nota são opcionais.
    Exemplos:
      "Lisboa"
      "Lisboa, 2022"
      "Lisboa, 2022, 9"

    Retorna: confirmação do registro.
    """
    partes = [p.strip() for p in info.split(",")]
    destino = partes[0]
    ano = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else None
    nota = int(partes[2]) if len(partes) > 2 and partes[2].isdigit() else None

    adicionar_visitado(destino, ano=ano, nota=nota)

    detalhes = []
    if ano:
        detalhes.append(f"ano: {ano}")
    if nota:
        detalhes.append(f"nota: {nota}/10")
    extras = f" ({', '.join(detalhes)})" if detalhes else ""

    return f"Registrado: {destino}{extras} adicionado ao histórico de viagens."


@tool
def list_visited(_: str = "") -> str:
    """
    Lista todos os destinos que o usuário já visitou.

    Use quando o usuário perguntar sobre suas viagens anteriores,
    ou quando quiser verificar o histórico completo antes de sugerir novos destinos.

    Não precisa de entrada — pode passar string vazia.
    """
    visitados = listar_visitados()

    if not visitados:
        return "Nenhum destino visitado registrado ainda. Peça ao usuário para informar suas viagens anteriores."

    from memoria.gerenciador import carregar_perfil
    perfil = carregar_perfil()

    linhas = [f"Destinos visitados ({len(visitados)} no total):\n"]
    for v in perfil["visitados"]:
        ano = v.get("ano", "?")
        nota = v.get("nota")
        nota_str = f" — nota {nota}/10" if nota else ""
        linhas.append(f"  • {v['destino']} ({ano}){nota_str}")

    return "\n".join(linhas)