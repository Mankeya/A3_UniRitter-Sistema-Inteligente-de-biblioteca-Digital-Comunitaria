"""Classe abstrata Pessoa - base de Leitor e Bibliotecario."""

from abc import ABC, abstractmethod
from datetime import datetime

from ..excecoes.erros import EntradaInvalidaError
from ..lgpd.cidadania_digital import gerar_hash_senha, registrar_consentimento


class Pessoa(ABC):
    """Usuario do sistema: ID, nome, CPF, e-mail, senha e consentimento."""

    __contador_id = 0

    def __init__(self, nome: str, cpf: str, email: str, id_pessoa: int = None):
        self.__id = id_pessoa if id_pessoa is not None else Pessoa._gerar_id()
        self.__nome = ""
        self.__cpf = ""
        self.__email = ""
        self.__senha_hash = ""
        self.__consentimento = {"aceito": False, "data_consentimento": None,
                                "finalidades": []}
        self.nome = nome
        self.cpf = cpf
        self.email = email

    @classmethod
    def _gerar_id(cls) -> int:
        """Gera o proximo ID unico de pessoa."""
        Pessoa.__contador_id += 1
        return Pessoa.__contador_id

    @classmethod
    def repor_contador(cls, maior_id: int) -> None:
        """Ajusta o contador de IDs apos carregar dados do JSON."""
        if maior_id > Pessoa.__contador_id:
            Pessoa.__contador_id = maior_id

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida o CPF pelos dois digitos verificadores."""
        digitos = "".join(c for c in cpf if c.isdigit())
        if len(digitos) != 11 or digitos == digitos[0] * 11:
            return False
        for tamanho in (9, 10):
            soma = sum(int(digitos[i]) * (tamanho + 1 - i) for i in range(tamanho))
            resto = (soma * 10) % 11
            resto = 0 if resto == 10 else resto
            if resto != int(digitos[tamanho]):
                return False
        return True

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida o formato do e-mail."""
        return "@" in email and "." in email.split("@")[-1] and len(email) >= 5

    @staticmethod
    def validar_data(data: str) -> bool:
        """Valida datas no formato dia/mes/ano."""
        try:
            datetime.strptime(data, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor: int):
        if not isinstance(valor, int) or valor <= 0:
            raise EntradaInvalidaError("O ID deve ser maior que 0.")
        self.__id = valor

    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise EntradaInvalidaError("O nome deve ser preenchido corretamente!")
        self.__nome = valor.strip()

    @property
    def cpf(self) -> str:
        return self.__cpf

    @cpf.setter
    def cpf(self, valor: str):
        if not Pessoa.validar_cpf(valor):
            raise EntradaInvalidaError("CPF invalido (verifique os digitos).")
        self.__cpf = "".join(c for c in valor if c.isdigit())

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        if not Pessoa.validar_email(valor):
            raise EntradaInvalidaError("E-mail invalido!")
        self.__email = valor.strip()

    @property
    def senha_hash(self) -> str:
        return self.__senha_hash

    @senha_hash.setter
    def senha_hash(self, valor: str):
        self.__senha_hash = valor

    @property
    def consentimento(self) -> dict:
        return self.__consentimento

    @consentimento.setter
    def consentimento(self, valor: dict):
        self.__consentimento = valor

    def definir_senha(self, senha: str) -> None:
        """Armazena a senha apenas como hash SHA-256."""
        if not senha or len(senha) < 4:
            raise EntradaInvalidaError("A senha deve ter no minimo 4 caracteres.")
        self.__senha_hash = gerar_hash_senha(senha)

    def aceitar_consentimento(self, aceito: bool) -> None:
        """Registra a decisao do usuario sobre o uso de seus dados."""
        self.__consentimento = registrar_consentimento(self.__consentimento, aceito)

    def anonimizar_dados(self) -> None:
        """Substitui os dados pessoais por valores nao identificaveis (LGPD)."""
        self.__nome = "Usuario Anonimizado"
        self.__cpf = "00000000000"
        self.__email = "anonimo@exemplo.com"
        self.__senha_hash = gerar_hash_senha("ANONIMIZADO")
        self.__consentimento = registrar_consentimento(self.__consentimento, False)

    @abstractmethod
    def tipo(self) -> str:
        """Retorna o tipo da pessoa."""
        pass

    @abstractmethod
    def dados_especificos(self) -> dict:
        """Retorna os campos proprios da subclasse."""
        pass

    def to_dict(self) -> dict:
        """Converte a pessoa em dicionario para o JSON."""
        dados = {
            "tipo": self.tipo(),
            "id": self.__id,
            "nome": self.__nome,
            "cpf": self.__cpf,
            "email": self.__email,
            "senha_hash": self.__senha_hash,
            "consentimento": self.__consentimento,
        }
        dados.update(self.dados_especificos())
        return dados

    def __str__(self) -> str:
        return f"[{self.tipo()}] {self.__nome} (ID {self.__id})"


def pessoa_from_dict(dados: dict):
    """Recria Leitor ou Bibliotecario a partir de um dicionario."""
    from .leitor import Leitor
    from .bibliotecario import Bibliotecario

    tipo = dados.get("tipo")
    comuns = {
        "nome": dados["nome"],
        "cpf": dados["cpf"],
        "email": dados["email"],
        "id_pessoa": dados["id"],
    }

    if tipo == "Leitor":
        pessoa = Leitor(
            data_nascimento=dados["data_nascimento"],
            limite_emprestimos=dados["limite_emprestimos"],
            **comuns,
        )
    elif tipo == "Bibliotecario":
        pessoa = Bibliotecario(
            matricula=dados["matricula"],
            setor=dados["setor"],
            **comuns,
        )
    else:
        raise EntradaInvalidaError(f"Tipo de pessoa desconhecido: {tipo}")

    pessoa.senha_hash = dados.get("senha_hash", "")
    pessoa.consentimento = dados.get(
        "consentimento", {"aceito": False, "data_consentimento": None,
                          "finalidades": []}
    )
    return pessoa
