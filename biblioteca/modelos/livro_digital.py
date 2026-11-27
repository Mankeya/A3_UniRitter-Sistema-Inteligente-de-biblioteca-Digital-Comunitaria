"""LivroDigital - herda de Material (RF02)."""

from .material import Material
from ..excecoes.erros import EntradaInvalidaError


class LivroDigital(Material):
    """Livro em arquivo digital (PDF, EPUB, MOBI etc.)."""

    FORMATOS_VALIDOS = ("PDF", "EPUB", "MOBI", "DJVU", "TXT")

    def __init__(self, isbn: str, titulo: str, autor: str,
                 tamanho_mb: float, formato: str,
                 total_exemplares: int = 1, id_material: int = None):
        super().__init__(titulo, autor, total_exemplares, id_material)
        self.__isbn = ""
        self.__tamanho_mb = 0.0
        self.__formato = ""
        self.isbn = isbn
        self.tamanho_mb = tamanho_mb
        self.formato = formato

    @property
    def isbn(self) -> str:
        return self.__isbn

    @isbn.setter
    def isbn(self, valor: str):
        digitos = "".join(c for c in valor if c.isalnum())
        if len(digitos) not in (10, 13):
            raise EntradaInvalidaError("ISBN invalido (10 ou 13 caracteres).")
        self.__isbn = valor.strip()

    @property
    def tamanho_mb(self) -> float:
        return self.__tamanho_mb

    @tamanho_mb.setter
    def tamanho_mb(self, valor):
        try:
            tamanho = float(valor)
        except (TypeError, ValueError):
            raise EntradaInvalidaError("O tamanho do arquivo deve ser numerico.")
        if tamanho <= 0:
            raise EntradaInvalidaError("O tamanho do arquivo deve ser maior que 0.")
        self.__tamanho_mb = round(tamanho, 2)

    @property
    def formato(self) -> str:
        return self.__formato

    @formato.setter
    def formato(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise EntradaInvalidaError("O formato do arquivo e obrigatorio.")
        self.__formato = valor.strip().upper()

    def calcular_multa(self, dias_atraso: int) -> float:
        """Livro digital: R$ 0,50 por dia de atraso."""
        if dias_atraso <= 0:
            return 0.0
        return dias_atraso * 0.50

    def tipo(self) -> str:
        return "Livro Digital"

    def dados_especificos(self) -> dict:
        return {
            "isbn": self.__isbn,
            "tamanho_mb": self.__tamanho_mb,
            "formato": self.__formato,
        }
