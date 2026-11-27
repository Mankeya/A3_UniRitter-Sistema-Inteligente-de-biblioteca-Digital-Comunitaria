"""Cidadania Digital e LGPD - desafio extra do projeto."""

import hashlib
import json
from datetime import datetime
from pathlib import Path

DIRETORIO_DADOS = Path(__file__).resolve().parent.parent / "dados"


def gerar_hash_senha(senha: str) -> str:
    """Retorna o hash SHA-256 da senha informada."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara uma senha em texto puro com o hash armazenado."""
    return gerar_hash_senha(senha) == senha_hash


def registrar_log(acao: str, usuario: str = "-", detalhe: str = "") -> None:
    """Registra uma operacao em logs.json (auditoria)."""
    DIRETORIO_DADOS.mkdir(parents=True, exist_ok=True)
    caminho = DIRETORIO_DADOS / "logs.json"

    logs = []
    if caminho.exists():
        try:
            logs = json.loads(caminho.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logs = []

    logs.append({
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "acao": acao,
        "usuario": usuario,
        "detalhe": detalhe,
    })

    caminho.write_text(
        json.dumps(logs, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def registrar_consentimento(consentimento: dict, aceito: bool) -> dict:
    """Registra a decisao do usuario sobre o uso de seus dados."""
    consentimento["aceito"] = aceito
    consentimento["data_consentimento"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    consentimento["finalidades"] = [
        "cadastro e autenticacao",
        "controle de emprestimos e reservas",
        "recomendacao de materiais",
    ] if aceito else []
    return consentimento


def anonimizar_usuario(usuario) -> None:
    """Anonimiza os dados pessoais, preservando o historico (LGPD)."""
    if hasattr(usuario, "anonimizar_dados"):
        usuario.anonimizar_dados()
        return

    if hasattr(usuario, "nome"):
        usuario.nome = "Usuario Anonimizado"
    if hasattr(usuario, "email"):
        usuario.email = "anonimo@exemplo.com"
    if hasattr(usuario, "senha_hash"):
        usuario.senha_hash = gerar_hash_senha("ANONIMIZADO")
    if hasattr(usuario, "consentimento"):
        usuario.consentimento = registrar_consentimento(
            getattr(usuario, "consentimento", {}), False
        )


def gerar_relatorio_uso(usuarios, materiais, emprestimos) -> dict:
    """Gera relatorio de uso e acessibilidade da plataforma."""
    caminho_logs = DIRETORIO_DADOS / "logs.json"
    logs = []
    if caminho_logs.exists():
        try:
            logs = json.loads(caminho_logs.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logs = []

    acoes = {}
    for entrada in logs:
        acao = entrada.get("acao", "desconhecida")
        acoes[acao] = acoes.get(acao, 0) + 1

    ativos = {e.get("usuario") for e in logs if e.get("usuario") not in (None, "-", "")}

    return {
        "total_acessos": len(logs),
        "usuarios_cadastrados": len(usuarios),
        "usuarios_ativos": len(ativos),
        "materiais_cadastrados": len(materiais),
        "emprestimos_registrados": len(emprestimos),
        "acoes_por_tipo": dict(sorted(acoes.items(), key=lambda x: x[1], reverse=True)),
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }


def formatar_relatorio_uso(relatorio: dict) -> str:
    """Converte o relatorio de uso em texto para o terminal."""
    linhas = [
        "=" * 55,
        "  RELATORIO DE ACESSIBILIDADE E USO DA PLATAFORMA (LGPD)",
        "=" * 55,
        f"  Acessos registrados ......... {relatorio['total_acessos']}",
        f"  Usuarios cadastrados ........ {relatorio['usuarios_cadastrados']}",
        f"  Usuarios ativos ............. {relatorio['usuarios_ativos']}",
        f"  Materiais cadastrados ....... {relatorio['materiais_cadastrados']}",
        f"  Emprestimos registrados ..... {relatorio['emprestimos_registrados']}",
        "-" * 55,
        "  Acoes mais executadas:",
    ]
    for acao, total in relatorio["acoes_por_tipo"].items():
        linhas.append(f"    - {acao}: {total}")
    linhas.append(f"  Gerado em: {relatorio['gerado_em']}")
    linhas.append("=" * 55)
    return "\n".join(linhas)
