"""
preferencias.py — Ferramentas de gestão de preferências

save_preference: salva uma preferência extraída da conversa
get_preferences: retorna todas as preferências conhecidas

O agente deve chamar save_preference sempre que o usuário declarar
algo sobre seus gostos — mesmo implicitamente.

Exemplos de inferência que o agente deve fazer:
  "Odeio calor" → save_preference("clima, ameno ou frio")
  "Estou com budget apertado" → save_preference("budget, baixo")
  "Prefiro lugares menos turísticos" → save_preference("agitacao, tranquilo")
"""

from langchain_core.tools import tool
from memoria import salvar_preferencia, obter_preferencias


# Preferências válidas — ajudam o agente a usar chaves consistentes
CHAVES_VALIDAS = {
    "tipo": ["praia", "natureza", "cultura", "gastronomia", "aventura", "descanso"],
    "budget": ["baixo", "médio", "alto"],
    "clima": ["frio", "ameno", "quente", "tropical"],
    "agitacao": ["tranquilo", "moderado", "agitado"],
    "duracao": ["fim de semana", "1 semana", "2 semanas", "longa"],
    "companhia": ["solo", "casal", "família", "amigos"],
}


@tool
def save_preference(preferencia: str) -> str:
    """
    Salva uma preferência do usuário para uso em sugestões futuras.

    Chame esta ferramenta sempre que o usuário mencionar algo sobre seus gostos,
    estilo de viagem, restrições ou expectativas — mesmo que implicitamente.

    Entrada esperada: "chave, valor" separados por vírgula.
    Exemplos:
      "tipo, praia"
      "budget, baixo"
      "clima, ameno"
      "agitacao, tranquilo"
      "companhia, casal"
      "duracao, 1 semana"

    Chaves recomendadas: tipo, budget, clima, agitacao, duracao, companhia

    Retorna: confirmação do que foi salvo.
    """
    partes = [p.strip() for p in preferencia.split(",", 1)]
    if len(partes) < 2:
        return "Formato inválido. Use: 'chave, valor' — ex: 'tipo, praia'"

    chave, valor = partes[0].lower(), partes[1].lower()
    salvar_preferencia(chave, valor)
    return f"Preferência salva: {chave} = {valor}. Será usada nas próximas sugestões."


@tool
def get_preferences(_: str = "") -> str:
    """
    Retorna todas as preferências conhecidas do usuário.

    Use antes de fazer uma busca por destinos, para incorporar o perfil
    completo do usuário nos critérios de filtragem.

    Não precisa de entrada — pode passar string vazia.
    """
    prefs = obter_preferencias()

    if not prefs:
        return (
            "Nenhuma preferência registrada ainda. "
            "Pergunte ao usuário sobre seus gostos para personalizar as sugestões."
        )

    linhas = ["Preferências conhecidas do usuário:\n"]
    for chave, valor in prefs.items():
        linhas.append(f"  • {chave}: {valor}")

    return "\n".join(linhas)