"""Interface (classe abstrata) Avaliavel - definida com ABC."""

from abc import ABC, abstractmethod


class Avaliavel(ABC):
    """Interface com as operacoes de avaliacao (nota de 1 a 5)."""

    @abstractmethod
    def avaliar(self, nota: int, comentario: str) -> None:
        """Registra uma avaliacao com nota e comentario opcional."""
        pass

    @abstractmethod
    def calcular_media(self) -> float:
        """Retorna a media das notas recebidas."""
        pass
