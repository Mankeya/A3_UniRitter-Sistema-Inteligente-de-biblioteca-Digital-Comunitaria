"""Emprestimo - ligacao entre usuario e material (RF03)."""

from datetime import datetime, timedelta

from ..excecoes.erros import EntradaInvalidaError


class Emprestimo:
    """Registra data de emprestimo, previsao de devolucao e multa."""

    DIAS_PRAZO_PADRAO = 7

    def __init__(self, id_emprestimo: int, id_usuario: int, cpf_usuario: str,
                 id_material: int, data_emprestimo: str = None,
                 data_prevista: str = None, data_devolucao: str = None,
                 multa: float = 0.0):
        self.__id = id_emprestimo
        self.__id_usuario = id_usuario
        self.__cpf_usuario = cpf_usuario
        self.__id_material = id_material
        self.__data_emprestimo = data_emprestimo or datetime.now().strftime("%d/%m/%Y")
        self.__data_prevista = data_prevista or (
            datetime.now() + timedelta(days=self.DIAS_PRAZO_PADRAO)
        ).strftime("%d/%m/%Y")
        self.__data_devolucao = data_devolucao
        self.__multa = multa

    @property
    def id(self) -> int:
        return self.__id

    @property
    def id_usuario(self) -> int:
        return self.__id_usuario

    @property
    def cpf_usuario(self) -> str:
        return self.__cpf_usuario

    @property
    def id_material(self) -> int:
        return self.__id_material

    @property
    def data_emprestimo(self) -> str:
        return self.__data_emprestimo

    @property
    def data_prevista(self) -> str:
        return self.__data_prevista

    @property
    def data_devolucao(self) -> str:
        return self.__data_devolucao

    @property
    def multa(self) -> float:
        return self.__multa

    @property
    def ativo(self) -> bool:
        """True enquanto o material nao foi devolvido."""
        return self.__data_devolucao is None

    def dias_atraso(self, data_devolucao: str = None) -> int:
        """Calcula os dias de atraso em relacao a data prevista."""
        fim = data_devolucao or datetime.now().strftime("%d/%m/%Y")
        try:
            prevista = datetime.strptime(self.__data_prevista, "%d/%m/%Y")
            devolvido = datetime.strptime(fim, "%d/%m/%Y")
        except ValueError:
            raise EntradaInvalidaError("Data invalida para calculo de atraso.")
        atraso = (devolvido - prevista).days
        return max(0, atraso)

    def registrar_devolucao(self, multa: float) -> str:
        """Encerra o emprestimo registrando data e multa."""
        if not self.ativo:
            raise EntradaInvalidaError("Este emprestimo ja foi devolvido.")
        self.__data_devolucao = datetime.now().strftime("%d/%m/%Y")
        self.__multa = round(multa, 2)
        return self.__data_devolucao

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "id_usuario": self.__id_usuario,
            "cpf_usuario": self.__cpf_usuario,
            "id_material": self.__id_material,
            "data_emprestimo": self.__data_emprestimo,
            "data_prevista": self.__data_prevista,
            "data_devolucao": self.__data_devolucao,
            "multa": self.__multa,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Emprestimo":
        return cls(
            id_emprestimo=dados["id"],
            id_usuario=dados["id_usuario"],
            cpf_usuario=dados["cpf_usuario"],
            id_material=dados["id_material"],
            data_emprestimo=dados["data_emprestimo"],
            data_prevista=dados["data_prevista"],
            data_devolucao=dados.get("data_devolucao"),
            multa=dados.get("multa", 0.0),
        )

    def __str__(self) -> str:
        situacao = "ATIVO" if self.ativo else f"devolvido em {self.__data_devolucao}"
        return (f"Emprestimo #{self.__id}: material {self.__id_material} "
                f"| usuario {self.__cpf_usuario} | {situacao}")
