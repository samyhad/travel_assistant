"""
main.py — Ponto de entrada do agente evolutivo de viagens

Loop de conversa interativo. A cada rodada:
  1. O perfil do usuário é carregado do disco
  2. O agente raciocina usando esse contexto
  3. Novas preferências e destinos visitados são salvos automaticamente
  4. Na próxima conversa, o agente já sabe mais sobre o usuário

Execute: python main.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agente import perguntar
from memoria import resumo_perfil, carregar_perfil


def exibir_perfil_atual():
    """Mostra o estado atual do perfil — útil para acompanhar a evolução."""
    perfil = carregar_perfil()
    print("\n" + "─" * 50)
    print("📋 Perfil atual do usuário:")

    visitados = perfil.get("visitados", [])
    if visitados:
        nomes = [v["destino"] for v in visitados]
        print(f"  Visitados: {', '.join(nomes)}")
    else:
        print("  Visitados: nenhum ainda")

    prefs = perfil.get("preferencias", {})
    if prefs:
        print("  Preferências:")
        for k, v in prefs.items():
            print(f"    • {k}: {v['valor']}")
    else:
        print("  Preferências: nenhuma ainda")
    print("─" * 50 + "\n")


def main():
    print("\n" + "=" * 60)
    print("🌍  Agente Evolutivo de Destinos Turísticos")
    print("=" * 60)
    print("Quanto mais você conversa, mais personalizado fica.")
    print("O agente aprende suas preferências e histórico de viagens.")
    print("\nComandos especiais:")
    print("  'perfil'  — mostra o perfil salvo até agora")
    print("  'limpar'  — reseta o perfil (começa do zero)")
    print("  'sair'    — encerra o programa")
    print("=" * 60)

    # Mostra o perfil atual ao iniciar (pode ter dados de sessões anteriores)
    exibir_perfil_atual()

    # Sugestões de perguntas para quem está testando pela primeira vez
    perfil = carregar_perfil()
    if not perfil["visitados"] and not perfil["preferencias"]:
        print("💡 Sugestões para começar:")
        print("  → 'Já fui a Lisboa e Amsterdã, quero algo com praia para outubro'")
        print("  → 'Tenho budget baixo e prefiro lugares tranquilos'")
        print("  → 'Quero uma semana de descanso em outubro, odeio calor excessivo'")
        print()

    while True:
        try:
            pergunta = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nAté a próxima viagem! ✈️")
            break

        if not pergunta:
            continue

        if pergunta.lower() == "sair":
            print("Até a próxima viagem! ✈️")
            break

        if pergunta.lower() == "perfil":
            exibir_perfil_atual()
            continue

        if pergunta.lower() == "limpar":
            from memoria.gerenciador import PERFIL_VAZIO, salvar_perfil
            salvar_perfil(PERFIL_VAZIO.copy())
            print("✅ Perfil resetado.\n")
            continue

        print()
        try:
            resposta = perguntar(pergunta)
            print("\n" + "─" * 60)
            print("🤖 Agente:")
            print(resposta)
            print("─" * 60 + "\n")
        except Exception as e:
            print(f"\n❌ Erro ao processar: {e}\n")


if __name__ == "__main__":
    main()