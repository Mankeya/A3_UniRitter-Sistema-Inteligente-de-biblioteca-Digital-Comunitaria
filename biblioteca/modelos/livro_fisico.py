"""LivroFisico - herda de Material (RF02)."""

from .material import Material
from ..excecoes.erros import EntradaInvalidaError


class LivroFisico(Material):
    """Livro impresso com exemplares fisicos em acervo."""

    def __init__(self, isbn: str, titulo: str, autor: str,
                 total_exemplares: int, id_material: int = None):
        super().__init__(titulo, autor, total_exemplares, id_material)
        self.__isbn = ""
        self.isbn = isbn

    @property
    def isbn(self) -> str:
        return self.__isbn

    @isbn.setter
    def isbn(self, valor: str):
        digitos = "".join(c for c in valor if c.isalnum())
        if len(digitos) not in (10, 13):
            raise EntradaInvalidaError("ISBN invalido (10 ou 13 caracteres).")
        self.__isbn = valor.strip()

    def calcular_multa(self, dias_atraso: int) -> float:
        """Livro fisico: R$ 1,00 por dia de atraso."""
        if dias_atraso <= 0:
            return 0.0
        return dias_atraso * 1.00

    def tipo(self) -> str:
        return "Livro Fisico"

    def dados_especificos(self) -> dict:
        return {"isbn": self.__isbn}
