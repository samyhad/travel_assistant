"""
gerenciador.py — Camada de memória persistente do agente.

Salva e lê um arquivo JSON com o perfil do usuário:
  - destinos visitados
  - preferências declaradas (tipo de viagem, clima, budget, etc.)
  - histórico de perguntas feitas ao agente

Propositalmente simples: um arquivo JSON é suficiente para demonstrar
o comportamento evolutivo. Em produção, troque por SQLite ou um banco vetorial.
"""

import json
import os
import threading
from datetime import datetime
from typing import Optional

CAMINHO_PERFIL = os.path.join(os.path.dirname(__file__), "perfil.json")
_lock_perfil = threading.Lock()

PERFIL_VAZIO = {
    "visitados": [],          # [{"destino": "Lisboa", "ano": 2022, "nota": 9}]
    "preferencias": {},       # {"tipo": "praia", "budget": "médio", "clima": "ameno"}
    "historico_perguntas": [], # últimas N perguntas feitas ao agente
}


# -----------------------------------------------------------------------------
# Leitura / escrita base
# -----------------------------------------------------------------------------

def _carregar_perfil_sem_lock() -> dict:
    """Leitura interna — use carregar_perfil() na aplicação."""
    if not os.path.exists(CAMINHO_PERFIL):
        return PERFIL_VAZIO.copy()

    with open(CAMINHO_PERFIL, "r", encoding="utf-8") as f:
        conteudo = f.read().strip()

    if not conteudo:
        return PERFIL_VAZIO.copy()

    try:
        return json.loads(conteudo)
    except json.JSONDecodeError:
        return PERFIL_VAZIO.copy()


def carregar_perfil() -> dict:
    """Carrega o perfil do disco. Se não existir ou estiver corrompido, cria um vazio."""
    with _lock_perfil:
        if not os.path.exists(CAMINHO_PERFIL):
            salvar_perfil(PERFIL_VAZIO.copy())
            return PERFIL_VAZIO.copy()
        return _carregar_perfil_sem_lock()


def salvar_perfil(perfil: dict) -> None:
    """Persiste o perfil no disco (escrita atômica para evitar corrupção)."""
    os.makedirs(os.path.dirname(CAMINHO_PERFIL), exist_ok=True)
    temp = CAMINHO_PERFIL + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=2)
    os.replace(temp, CAMINHO_PERFIL)


# -----------------------------------------------------------------------------
# Destinos visitados
# -----------------------------------------------------------------------------

def adicionar_visitado(destino: str, ano: Optional[int] = None, nota: Optional[int] = None) -> None:
    """Registra que o usuário visitou um destino."""
    with _lock_perfil:
        perfil = _carregar_perfil_sem_lock()

        for v in perfil["visitados"]:
            if v["destino"].lower() == destino.lower():
                if ano:
                    v["ano"] = ano
                if nota:
                    v["nota"] = nota
                salvar_perfil(perfil)
                return

        entrada = {"destino": destino, "adicionado_em": datetime.now().isoformat()}
        if ano:
            entrada["ano"] = ano
        if nota:
            entrada["nota"] = nota

        perfil["visitados"].append(entrada)
        salvar_perfil(perfil)


def listar_visitados() -> list[str]:
    """Retorna lista de nomes dos destinos visitados."""
    perfil = carregar_perfil()
    return [v["destino"] for v in perfil["visitados"]]


def foi_visitado(destino: str) -> bool:
    return destino.lower() in [v.lower() for v in listar_visitados()]


# -----------------------------------------------------------------------------
# Preferências
# -----------------------------------------------------------------------------

def salvar_preferencia(chave: str, valor: str) -> None:
    """
    Salva ou atualiza uma preferência do usuário.
    Exemplos: chave="tipo", valor="praia"
               chave="budget", valor="baixo"
               chave="clima", valor="tropical"
    """
    with _lock_perfil:
        perfil = _carregar_perfil_sem_lock()
        valor_final = valor
        if chave in perfil["preferencias"]:
            atual = perfil["preferencias"][chave]["valor"]
            # Chaves como "tipo" podem ter vários valores (praia, natureza, ...)
            if chave == "tipo" and valor.lower() not in atual.lower():
                valor_final = f"{atual}, {valor}"
        perfil["preferencias"][chave] = {
            "valor": valor_final,
            "atualizado_em": datetime.now().isoformat(),
        }
        salvar_perfil(perfil)


def obter_preferencias() -> dict:
    """Retorna dict de preferências {chave: valor}."""
    perfil = carregar_perfil()
    return {k: v["valor"] for k, v in perfil["preferencias"].items()}


# -----------------------------------------------------------------------------
# Histórico de perguntas
# -----------------------------------------------------------------------------

def registrar_pergunta(pergunta: str) -> None:
    """Salva a pergunta no histórico (mantém os últimos 20 registros)."""
    with _lock_perfil:
        perfil = _carregar_perfil_sem_lock()
        perfil["historico_perguntas"].append({
            "pergunta": pergunta,
            "data": datetime.now().isoformat(),
        })
        perfil["historico_perguntas"] = perfil["historico_perguntas"][-20:]
        salvar_perfil(perfil)


def resumo_perfil() -> str:
    """
    Retorna um resumo em texto do perfil — usado para injetar contexto
    no prompt do agente antes de cada conversa.
    """
    perfil = carregar_perfil()

    visitados = [v["destino"] for v in perfil["visitados"]]
    prefs = {k: v["valor"] for k, v in perfil["preferencias"].items()}

    partes = []

    if visitados:
        partes.append(f"Destinos já visitados: {', '.join(visitados)}.")
    else:
        partes.append("Nenhum destino visitado registrado ainda.")

    if prefs:
        prefs_str = ", ".join(f"{k}: {v}" for k, v in prefs.items())
        partes.append(f"Preferências conhecidas: {prefs_str}.")
    else:
        partes.append("Nenhuma preferência registrada ainda.")

    return " ".join(partes)