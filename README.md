# Agente Evolutivo de Destinos Turísticos

## Estrutura do projeto

```
agente_viagens/
├── README.md
├── requirements.txt
├── main.py                  # Ponto de entrada — loop de conversa
├── agente.py                # Agente ReAct (LangGraph)
├── memoria/
│   ├── __init__.py
│   ├── gerenciador.py       # Lê/escreve perfil do usuário em JSON
│   └── perfil.json          # Criado automaticamente na primeira execução
└── ferramentas/
    ├── __init__.py
    ├── busca.py             # search_by_profile — filtra destinos por atributos
    ├── comparacao.py        # compare_destinations — cruza dados entre destinos
    ├── historico.py         # check_visited / save_visited — controle de viagens
    └── preferencias.py      # save_preference / get_preferences — gostos do usuário
```

## Instalação

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto (já está no `.gitignore`):

```
OPENAI_API_KEY=sua-chave
```

No Windows (PowerShell), em vez do `.env` você pode usar:

```powershell
$env:OPENAI_API_KEY="sua-chave"
```

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```

O agente usa **LangChain 1.x** (`create_agent`), que compila um grafo **LangGraph** — API atual recomendada (substitui o `create_react_agent` depreciado). Você pode evoluir com middleware, checkpointing ou nós customizados.

## O que testar

1. **Primeira conversa**: diga que já foi a Lisboa e que gosta de praias tranquilas
2. **Segunda conversa**: peça uma sugestão de destino — o agente já saberá o seu histórico
3. **Refine**: diga que o budget é baixo e veja o ranking mudar
4. **Evolução**: após cada conversa, abra `memoria/perfil.json` e veja o que foi salvo