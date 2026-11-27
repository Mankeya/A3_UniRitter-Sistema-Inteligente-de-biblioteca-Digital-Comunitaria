"""Revista - herda de Material (RF02)."""

from .material import Material
from ..excecoes.erros import EntradaInvalidaError


class Revista(Material):
    """Publicacao periodica identificada por ISSN e edicao."""

    def __init__(self, issn: str, titulo: str, edicao: str,
                 autor: str = "N/A", total_exemplares: int = 1,
                 id_material: int = None):
        super().__init__(titulo, autor, total_exemplares, id_material)
        self.__issn = ""
        self.__edicao = ""
        self.issn = issn
        self.edicao = edicao

    @property
    def issn(self) -> str:
        return self.__issn

    @issn.setter
    def issn(self, valor: str):
        digitos = "".join(c for c in valor if c.isalnum())
        if len(digitos) != 8:
            raise EntradaInvalidaError("ISSN invalido (8 caracteres).")
        self.__issn = valor.strip()

    @property
    def edicao(self) -> str:
        return self.__edicao

    @edicao.setter
    def edicao(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise EntradaInvalidaError("A edicao da revista e obrigatoria.")
        self.__edicao = valor.strip()

    def calcular_multa(self, dias_atraso: int) -> float:
        """Revista: R$ 0,75 por dia de atraso."""
        if dias_atraso <= 0:
            return 0.0
        return dias_atraso * 0.75

    def tipo(self) -> str:
        return "Revista"

    def dados_especificos(self) -> dict:
        return {
            "issn": self.__issn,
            "edicao": self.__edicao,
        }
