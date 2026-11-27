"""Classe Bibliotecario - herda de Pessoa (RF01)."""

from .pessoa import Pessoa
from ..excecoes.erros import EntradaInvalidaError


class Bibliotecario(Pessoa):
    """Funcionario que administra a biblioteca."""

    def __init__(self, nome: str, cpf: str, email: str,
                 matricula: str, setor: str, id_pessoa: int = None):
        super().__init__(nome, cpf, email, id_pessoa)
        self.__matricula = ""
        self.__setor = ""
        self.matricula = matricula
        self.setor = setor

    @property
    def matricula(self) -> str:
        return self.__matricula

    @matricula.setter
    def matricula(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise EntradaInvalidaError("A matricula funcional e obrigatoria.")
        self.__matricula = valor.strip()

    @property
    def setor(self) -> str:
        return self.__setor

    @setor.setter
    def setor(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise EntradaInvalidaError("O setor e obrigatorio.")
        self.__setor = valor.strip()

    def tipo(self) -> str:
        return "Bibliotecario"

    def dados_especificos(self) -> dict:
        return {
            "matricula": self.__matricula,
            "setor": self.__setor,
        }
