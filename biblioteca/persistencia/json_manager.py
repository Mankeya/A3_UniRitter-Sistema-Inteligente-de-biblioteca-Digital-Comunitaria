"""Gerenciador de arquivos JSON (persistencia de dados)."""

import json
from pathlib import Path

DIRETORIO_DADOS = Path(__file__).resolve().parent.parent / "dados"

ARQUIVOS = {
    "usuarios": [],
    "materiais": [],
    "emprestimos": [],
    "avaliacoes": [],
    "fila_reservas": [],
    "logs": [],
}


def _caminho(nome_arquivo: str) -> Path:
    """Retorna o caminho completo de um arquivo JSON."""
    if not nome_arquivo.endswith(".json"):
        nome_arquivo = f"{nome_arquivo}.json"
    return DIRETORIO_DADOS / nome_arquivo


def garantir_arquivos() -> None:
    """Cria o diretorio e os arquivos JSON vazios, se preciso."""
    DIRETORIO_DADOS.mkdir(parents=True, exist_ok=True)
    for nome, padrao in ARQUIVOS.items():
        caminho = _caminho(nome)
        if not caminho.exists():
            caminho.write_text(
                json.dumps(padrao, ensure_ascii=False, indent=4),
                encoding="utf-8",
            )


def carregar(nome_arquivo: str):
    """Le um arquivo JSON; retorna o padrao se estiver vazio/corrompido."""
    garantir_arquivos()
    caminho = _caminho(nome_arquivo)
    try:
        conteudo = caminho.read_text(encoding="utf-8").strip()
        if not conteudo:
            return ARQUIVOS.get(nome_arquivo, [])
        return json.loads(conteudo)
    except (json.JSONDecodeError, OSError):
        return ARQUIVOS.get(nome_arquivo, [])


def salvar(nome_arquivo: str, dados) -> None:
    """Grava a estrutura em JSON (sobrescreve o arquivo)."""
    garantir_arquivos()
    caminho = _caminho(nome_arquivo)
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def salvar_todos(usuarios: list, materiais: list, emprestimos: list,
                 avaliacoes: list, fila_reservas=()) -> None:
    """Salva as cinco estruturas principais de uma vez."""
    salvar("usuarios", [p.to_dict() for p in usuarios])
    salvar("materiais", [m.to_dict() for m in materiais])
    salvar("emprestimos", [e.to_dict() for e in emprestimos])
    salvar("avaliacoes", avaliacoes)
    salvar("fila_reservas", [list(reserva) for reserva in fila_reservas])
