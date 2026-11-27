"""Classe abstrata Material - base dos materiais (RF02)."""

from abc import ABC, abstractmethod

from .avaliavel import Avaliavel
from ..excecoes.erros import AvaliacaoInvalidaError, EntradaInvalidaError


class Material(Avaliavel, ABC):
    """Material bibliografico: titulo, autor, exemplares e avaliacoes."""

    __contador_id = 0

    def __init__(self, titulo: str, autor: str, total_exemplares: int,
                 id_material: int = None):
        self.__id = id_material if id_material is not None else Material._gerar_id()
        self.__titulo = ""
        self.__autor = ""
        self.__total_exemplares = 0
        self.__exemplares_disponiveis = 0
        self.__exemplares_reservados = 0
        self.__total_emprestimos = 0
        self.__avaliacoes = []
        self.titulo = titulo
        self.autor = autor
        self.total_exemplares = total_exemplares

    @classmethod
    def _gerar_id(cls) -> int:
        """Gera o proximo ID unico de material."""
        Material.__contador_id += 1
        return Material.__contador_id

    @classmethod
    def repor_contador(cls, maior_id: int) -> None:
        """Ajusta o contador de IDs apos carregar dados do JSON."""
        if maior_id > Material.__contador_id:
            Material.__contador_id = maior_id

    @property
    def id(self) -> int:
        return self.__id

    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise EntradaInvalidaError("O titulo do material e obrigatorio.")
        self.__titulo = valor.strip()

    @property
    def autor(self) -> str:
        return self.__autor

    @autor.setter
    def autor(self, valor: str):
        self.__autor = valor.strip() if valor and valor.strip() else "N/A"

    @property
    def total_exemplares(self) -> int:
        return self.__total_exemplares

    @total_exemplares.setter
    def total_exemplares(self, valor: int):
        if not isinstance(valor, int) or valor <= 0:
            raise EntradaInvalidaError(
                "A quantidade de exemplares deve ser maior que 0."
            )
        self.__total_exemplares = valor
        self.__exemplares_disponiveis = valor

    @property
    def exemplares_disponiveis(self) -> int:
        return self.__exemplares_disponiveis

    @property
    def exemplares_reservados(self) -> int:
        """Exemplares devolvidos e ja segurados para a fila de reservas."""
        return self.__exemplares_reservados

    def adicionar_disponivel(self, quantidade: int = 1) -> None:
        """Devolve exemplares ao acervo (devolucao)."""
        teto = self.__total_exemplares - self.__exemplares_reservados
        self.__exemplares_disponiveis = min(
            self.__exemplares_disponiveis + quantidade, teto
        )

    def remover_disponivel(self, quantidade: int = 1) -> None:
        """Retira exemplares do acervo (emprestimo)."""
        if self.__exemplares_disponiveis < quantidade:
            raise EntradaInvalidaError("Quantidade de exemplares insuficiente.")
        self.__exemplares_disponiveis -= quantidade

    def segregar_para_reserva(self) -> None:
        """Devolucao com fila ativa: o exemplar nao volta ao acervo geral
        e fica reservado para o proximo usuario da fila (RF04)."""
        self.__exemplares_reservados += 1

    def atender_reserva(self) -> None:
        """Emprestimo atendido pela reserva: consome o exemplar segurado."""
        if self.__exemplares_reservados <= 0:
            raise EntradaInvalidaError(
                f"Nao ha exemplar segurado de '{self.__titulo}'."
            )
        self.__exemplares_reservados -= 1

    @property
    def total_emprestimos(self) -> int:
        return self.__total_emprestimos

    def registrar_emprestimo(self) -> None:
        """Incrementa o contador usado nas recomendacoes (RF06)."""
        self.__total_emprestimos += 1

    @property
    def avaliacoes(self) -> list:
        return list(self.__avaliacoes)

    def avaliar(self, nota: int, comentario: str) -> None:
        """Registra uma avaliacao de 1 a 5 (RF05)."""
        if not isinstance(nota, int) or not 1 <= nota <= 5:
            raise AvaliacaoInvalidaError("A nota deve ser um inteiro de 1 a 5.")
        self.__avaliacoes.append({
            "nota": nota,
            "comentario": comentario.strip(),
        })

    def calcular_media(self) -> float:
        """Retorna a media das notas (0.0 sem avaliacoes)."""
        if not self.__avaliacoes:
            return 0.0
        total = sum(avaliacao["nota"] for avaliacao in self.__avaliacoes)
        return round(total / len(self.__avaliacoes), 2)

    @property
    def total_avaliacoes(self) -> int:
        return len(self.__avaliacoes)

    def restaurar_avaliacoes(self, lista: list) -> None:
        """Restaura as avaliacoes carregadas do JSON."""
        self.__avaliacoes = list(lista)

    def ajustar_estado(self, disponiveis: int, total_emprestimos: int,
                       reservados: int = 0) -> None:
        """Restaura disponibilidade, reservas e contadores ao carregar do JSON."""
        if not 0 <= disponiveis <= self.__total_exemplares:
            raise EntradaInvalidaError(
                f"Quantidade disponivel invalida para '{self.__titulo}'."
            )
        if not 0 <= reservados <= self.__total_exemplares:
            raise EntradaInvalidaError(
                f"Quantidade reservada invalida para '{self.__titulo}'."
            )
        self.__exemplares_disponiveis = disponiveis
        self.__exemplares_reservados = reservados
        self.__total_emprestimos = max(0, total_emprestimos)

    @abstractmethod
    def calcular_multa(self, dias_atraso: int) -> float:
        """Calcula a multa de atraso (regra propria de cada subclasse)."""
        pass

    @abstractmethod
    def tipo(self) -> str:
        """Retorna o tipo do material."""
        pass

    @abstractmethod
    def dados_especificos(self) -> dict:
        """Retorna os campos proprios da subclasse."""
        pass

    def to_dict(self) -> dict:
        """Converte o material em dicionario para o JSON."""
        dados = {
            "tipo": self.tipo(),
            "id": self.__id,
            "titulo": self.__titulo,
            "autor": self.__autor,
            "total_exemplares": self.__total_exemplares,
            "exemplares_disponiveis": self.__exemplares_disponiveis,
            "exemplares_reservados": self.__exemplares_reservados,
            "total_emprestimos": self.__total_emprestimos,
            "avaliacoes": self.__avaliacoes,
        }
        dados.update(self.dados_especificos())
        return dados

    def __str__(self) -> str:
        return (f"[{self.tipo()}] {self.__titulo} - {self.__autor} "
                f"(ID {self.__id}, disponiveis: {self.__exemplares_disponiveis})")


def material_from_dict(dados: dict):
    """Recria o material correto (fisico, digital ou revista) pelo JSON."""
    from .livro_fisico import LivroFisico
    from .livro_digital import LivroDigital
    from .revista import Revista

    tipo = dados.get("tipo")
    comuns = {
        "titulo": dados["titulo"],
        "autor": dados.get("autor", "N/A"),
        "total_exemplares": dados["total_exemplares"],
        "id_material": dados["id"],
    }

    if tipo == "Livro Fisico":
        material = LivroFisico(isbn=dados["isbn"], **comuns)
    elif tipo == "Livro Digital":
        material = LivroDigital(
            isbn=dados["isbn"],
            tamanho_mb=dados["tamanho_mb"],
            formato=dados["formato"],
            **comuns,
        )
    elif tipo == "Revista":
        material = Revista(
            issn=dados["issn"],
            edicao=dados["edicao"],
            **comuns,
        )
    else:
        raise EntradaInvalidaError(f"Tipo de material desconhecido: {tipo}")

    material.ajustar_estado(
        disponiveis=dados.get("exemplares_disponiveis",
                              dados["total_exemplares"]),
        total_emprestimos=dados.get("total_emprestimos", 0),
        reservados=dados.get("exemplares_reservados", 0),
    )
    material.restaurar_avaliacoes(dados.get("avaliacoes", []))
    return material
