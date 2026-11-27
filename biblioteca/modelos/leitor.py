"""Classe Leitor - herda de Pessoa (RF01)."""

from .pessoa import Pessoa
from ..excecoes.erros import EntradaInvalidaError


class Leitor(Pessoa):
    """Usuario que realiza emprestimos de materiais."""

    def __init__(self, nome: str, cpf: str, email: str,
                 data_nascimento: str, limite_emprestimos: int = 3,
                 id_pessoa: int = None):
        super().__init__(nome, cpf, email, id_pessoa)
        self.__data_nascimento = ""
        self.__limite_emprestimos = 0
        self.data_nascimento = data_nascimento
        self.limite_emprestimos = limite_emprestimos

    @property
    def data_nascimento(self) -> str:
        return self.__data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, valor: str):
        if not Pessoa.validar_data(valor):
            raise EntradaInvalidaError(
                "Data de nascimento invalida (use dia/mes/ano)."
            )
        self.__data_nascimento = valor

    @property
    def limite_emprestimos(self) -> int:
        return self.__limite_emprestimos

    @limite_emprestimos.setter
    def limite_emprestimos(self, valor: int):
        if not isinstance(valor, int) or valor <= 0:
            raise EntradaInvalidaError(
                "O limite de emprestimos deve ser maior que 0."
            )
        self.__limite_emprestimos = valor

    def tipo(self) -> str:
        return "Leitor"

    def dados_especificos(self) -> dict:
        return {
            "data_nascimento": self.__data_nascimento,
            "limite_emprestimos": self.__limite_emprestimos,
        }
