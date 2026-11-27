"""Excecoes personalizadas do sistema de biblioteca."""


class MaterialIndisponivelError(Exception):
    """Nao ha exemplares disponiveis do material solicitado."""


class LimiteEmprestimosError(Exception):
    """O usuario atingiu o limite de emprestimos simultaneos."""


class AvaliacaoInvalidaError(Exception):
    """Nota fora do intervalo de 1 a 5 ou avaliacao indevida."""


class UsuarioNaoEncontradoError(Exception):
    """Nenhum usuario cadastrado com o CPF informado."""


class MaterialNaoEncontradoError(Exception):
    """Nenhum material cadastrado com o ID informado."""


class EntradaInvalidaError(Exception):
    """Valor digitado pelo usuario invalido."""


class ReservaJaRealizadaError(Exception):
    """O usuario ja possui reserva em aberto para o material."""


class EmprestimoNaoEncontradoError(Exception):
    """Nao existe emprestimo ativo para o usuario informado."""
