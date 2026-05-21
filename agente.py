"""
agente.py — Agente ReAct com LangGraph (via LangChain 1.x)

Usa create_agent (substituto atual de create_react_agent):
  - Grafo LangGraph compilado
  - Middleware extensível para evoluções futuras
  - Perfil do usuário injetado no system_prompt a cada pergunta
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

from ferramentas import TODAS_AS_FERRAMENTAS
from memoria import resumo_perfil, registrar_pergunta

load_dotenv()

# -----------------------------------------------------------------------------
# Modelo
# -----------------------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY"),
)

PROMPT_SISTEMA = """Você é um agente especialista em viagens. Seu objetivo é ajudar o usuário
a encontrar o próximo destino ideal com base no histórico e nas preferências dele.

PERFIL DO USUÁRIO (atualizado automaticamente):
{perfil_usuario}

INSTRUÇÕES IMPORTANTES:
- Sempre consulte as preferências (get_preferences) antes de buscar destinos.
- Sempre verifique destinos visitados (check_visited) antes de sugerir um lugar.
- Quando o usuário mencionar que já visitou algum lugar, salve com save_visited.
- Quando o usuário mencionar preferências (clima, budget, tipo), salve com save_preference.
- Use search_by_profile para encontrar candidatos, depois compare_destinations para decidir.
- Suas respostas finais devem incluir: top 3 destinos, justificativa e por que cada um
  é compatível com o perfil do usuário."""


# -----------------------------------------------------------------------------
# Agente — recriado a cada pergunta para injetar o perfil atual
# -----------------------------------------------------------------------------

def criar_agente(perfil_usuario: str):
    """Monta o grafo do agente (LangGraph) com o perfil do usuário no system prompt."""
    system_prompt = PROMPT_SISTEMA.format(perfil_usuario=perfil_usuario)
    return create_agent(
        model=llm,
        tools=TODAS_AS_FERRAMENTAS,
        system_prompt=system_prompt,
    )


def _imprimir_mensagem(msg) -> None:
    """Exibe uma mensagem do grafo no terminal (modo verbose)."""
    if isinstance(msg, AIMessage):
        if msg.tool_calls:
            for tc in msg.tool_calls:
                nome = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "?")
                args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})
                print(f"  → Ferramenta: {nome}({args})")
        elif msg.content:
            trecho = str(msg.content)[:200]
            if len(str(msg.content)) > 200:
                trecho += "..."
            print(f"  → Assistente: {trecho}")
    elif isinstance(msg, ToolMessage):
        trecho = str(msg.content)[:300]
        if len(str(msg.content)) > 300:
            trecho += "..."
        print(f"  ← Resultado: {trecho}")


def perguntar(pergunta: str, verbose: bool = True) -> str:
    """
    Recebe uma pergunta, injeta o perfil atual, executa o agente
    e retorna a resposta final do assistente.
    """
    registrar_pergunta(pergunta)

    perfil_atual = resumo_perfil()
    agente = criar_agente(perfil_atual)
    entrada = {"messages": [HumanMessage(content=pergunta)]}
    config = {"recursion_limit": 25}

    resultado = None
    mensagens_exibidas = 0

    for estado in agente.stream(entrada, config=config, stream_mode="values"):
        resultado = estado
        if verbose:
            novas = estado["messages"][mensagens_exibidas:]
            for msg in novas:
                _imprimir_mensagem(msg)
            mensagens_exibidas = len(estado["messages"])

    if not resultado:
        return ""

    mensagens = resultado["messages"]
    for msg in reversed(mensagens):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            return str(msg.content)

    ultima = mensagens[-1]
    return str(ultima.content) if ultima.content else ""
