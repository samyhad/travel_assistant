"""
agente.py — Montagem do agente ReAct

Aqui acontece a integração entre:
  - O LLM (raciocínio)
  - As ferramentas (ações)
  - A memória (contexto persistente injetado no prompt)

O ponto mais importante desta versão evolutiva é a injeção de contexto:
antes de cada pergunta, o resumo do perfil do usuário é adicionado ao
prompt — assim o agente sabe o que já foi visitado e quais são as
preferências conhecidas sem precisar perguntar de novo.
"""

import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain import hub
from langchain_core.prompts import PromptTemplate

from ferramentas import TODAS_AS_FERRAMENTAS
from memoria import resumo_perfil, registrar_pergunta


# -----------------------------------------------------------------------------
# Modelo
# -----------------------------------------------------------------------------

llm = ChatAnthropic(
    model="claude-opus-4-5",
    temperature=0,
    api_key=os.environ["ANTHROPIC_API_KEY"],
)

# Para OpenAI, substitua por:
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o", temperature=0)


# -----------------------------------------------------------------------------
# Prompt base (ReAct padrão do LangChain Hub)
# Vamos estender o template padrão para incluir o perfil do usuário.
# -----------------------------------------------------------------------------

TEMPLATE_COM_PERFIL = """Você é um agente especialista em viagens. Seu objetivo é ajudar o usuário
a encontrar o próximo destino ideal com base no histórico e nas preferências dele.

PERFIL DO USUÁRIO (atualizado automaticamente):
{perfil_usuario}

Você tem acesso às seguintes ferramentas:

{tools}

INSTRUÇÕES IMPORTANTES:
- Sempre consulte as preferências (get_preferences) antes de buscar destinos.
- Sempre verifique destinos visitados (check_visited) antes de sugerir um lugar.
- Quando o usuário mencionar que já visitou algum lugar, salve com save_visited.
- Quando o usuário mencionar preferências (clima, budget, tipo), salve com save_preference.
- Use search_by_profile para encontrar candidatos, depois compare_destinations para decidir.
- Suas respostas finais devem incluir: top 3 destinos, justificativa e por que cada um
  é compatível com o perfil do usuário.

Use o seguinte formato:

Question: a pergunta do usuário
Thought: o que preciso descobrir ou fazer
Action: nome da ferramenta (uma de: {tool_names})
Action Input: entrada para a ferramenta
Observation: resultado da ferramenta
... (repita Thought/Action/Observation quantas vezes precisar)
Thought: agora sei a resposta final
Final Answer: resposta completa e personalizada para o usuário

Comece!

Question: {input}
Thought: {agent_scratchpad}"""


# -----------------------------------------------------------------------------
# Fábrica do executor — recriado a cada pergunta para injetar o perfil atual
# -----------------------------------------------------------------------------

def criar_executor() -> AgentExecutor:
    """
    Cria um novo AgentExecutor com o perfil do usuário atualizado.
    Chamado a cada nova pergunta para garantir que o contexto está fresco.
    """
    prompt = PromptTemplate.from_template(TEMPLATE_COM_PERFIL)

    agente = create_react_agent(
        llm=llm,
        tools=TODAS_AS_FERRAMENTAS,
        prompt=prompt,
    )

    return AgentExecutor(
        agent=agente,
        tools=TODAS_AS_FERRAMENTAS,
        verbose=True,           # Mostra o loop ReAct no terminal
        max_iterations=12,      # Mais iterações que o original — perfil evolutivo exige mais ciclos
        handle_parsing_errors=True,
    )


def perguntar(pergunta: str) -> str:
    """
    Interface principal: recebe uma pergunta, injeta o perfil atual,
    executa o agente e retorna a resposta final.
    """
    registrar_pergunta(pergunta)

    perfil_atual = resumo_perfil()
    executor = criar_executor()

    resultado = executor.invoke({
        "input": pergunta,
        "perfil_usuario": perfil_atual,
    })

    return resultado["output"]