"""Interface de terminal do Sistema de Biblioteca Digital Comunitaria.

Estruturas de dados exigidas pelo enunciado:
    usuarios = []                    (list)
    materiais = []                   (list)
    emprestimos = []                 (list)
    fila_reservas = deque()          (queue)
    historico_emprestimos = {}       (dictionary)
"""

from collections import deque
from datetime import datetime

from .excecoes.erros import (
    AvaliacaoInvalidaError,
    EmprestimoNaoEncontradoError,
    EntradaInvalidaError,
    LimiteEmprestimosError,
    MaterialIndisponivelError,
    MaterialNaoEncontradoError,
    ReservaJaRealizadaError,
    UsuarioNaoEncontradoError,
)
from .lgpd import cidadania_digital as lgpd
from .modelos.bibliotecario import Bibliotecario
from .modelos.emprestimo import Emprestimo
from .modelos.leitor import Leitor
from .modelos.material import material_from_dict
from .modelos.pessoa import Pessoa, pessoa_from_dict
from .persistencia import json_manager

usuarios: list = []
materiais: list = []
emprestimos: list = []
fila_reservas = deque()
historico_emprestimos: dict = {}
avaliacoes: list = []

SEPARADOR = "-" * 58

# Persistencia
def carregar_dados() -> None:
    """Carrega todos os dados dos arquivos JSON na inicializacao."""
    global avaliacoes

    usuarios.clear()
    materiais.clear()
    emprestimos.clear()
    fila_reservas.clear()
    historico_emprestimos.clear()

    for dados in json_manager.carregar("usuarios"):
        usuarios.append(pessoa_from_dict(dados))

    for dados in json_manager.carregar("materiais"):
        materiais.append(material_from_dict(dados))

    for dados in json_manager.carregar("emprestimos"):
        emprestimos.append(Emprestimo.from_dict(dados))

    avaliacoes = list(json_manager.carregar("avaliacoes"))

    for reserva in json_manager.carregar("fila_reservas"):
        try:
            fila_reservas.append((str(reserva[0]), int(reserva[1])))
        except (TypeError, ValueError, IndexError):
            continue

    for emprestimo in emprestimos:
        historico_emprestimos.setdefault(emprestimo.cpf_usuario, []).append(
            emprestimo.id
        )

    if usuarios:
        Pessoa.repor_contador(max(p.id for p in usuarios))
    if materiais:
        from .modelos.material import Material
        Material.repor_contador(max(m.id for m in materiais))

def salvar_dados() -> None:
    """Grava todas as estruturas nos arquivos JSON."""
    json_manager.salvar_todos(usuarios, materiais, emprestimos, avaliacoes,
                               fila_reservas)

# Buscas auxiliares
def buscar_usuario(cpf: str) -> Pessoa:
    """Localiza um usuario pelo CPF."""
    cpf_limpo = "".join(c for c in cpf if c.isdigit())
    for usuario in usuarios:
        if usuario.cpf == cpf_limpo:
            return usuario
    raise UsuarioNaoEncontradoError(f"Nenhum usuario com CPF {cpf_limpo}.")

def buscar_material(id_material: int):
    """Localiza um material pelo ID."""
    for material in materiais:
        if material.id == id_material:
            return material
    raise MaterialNaoEncontradoError(f"Nenhum material com ID {id_material}.")

def emprestimos_ativos_do(cpf: str) -> list:
    """Retorna os emprestimos ainda nao devolvidos de um usuario."""
    return [e for e in emprestimos if e.cpf_usuario == cpf and e.ativo]

def usuario_devolveu(cpf: str, id_material: int) -> bool:
    """Verifica se o usuario ja devolveu aquele material (RF05)."""
    return any(
        e.cpf_usuario == cpf
        and e.id_material == id_material
        and not e.ativo
        for e in emprestimos
    )

def proximo_id_emprestimo() -> int:
    """Gera o proximo ID sequencial para emprestimos."""
    return max((e.id for e in emprestimos), default=0) + 1

# Entrada de dados validada
def ler_texto(mensagem: str) -> str:
    """Le uma linha nao vazia do terminal."""
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("  [ERRO] O campo nao pode ficar vazio.")

def ler_inteiro(mensagem: str, minimo: int = None, maximo: int = None) -> int:
    """Le um inteiro validado, repetindo ate o usuario acertar."""
    while True:
        valor = input(mensagem).strip()
        try:
            numero = int(valor)
        except ValueError:
            print("  [ERRO] Digite apenas numeros inteiros.")
            continue
        if minimo is not None and numero < minimo:
            print(f"  [ERRO] O valor minimo e {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"  [ERRO] O valor maximo e {maximo}.")
            continue
        return numero

def ler_confirmacao(mensagem: str) -> bool:
    """Le uma resposta sim/nao."""
    while True:
        valor = input(f"{mensagem} [s/N]: ").strip().lower()
        if valor in ("s", "sim", "n", "nao"):
            return valor in ("s", "sim")
        print("  [ERRO] Responda com 's' (sim) ou 'n' (nao).")

# RF01 - Cadastro de usuarios
def op_cadastrar_usuario() -> None:
    print(SEPARADOR)
    print("  RF01 - CADASTRO DE USUARIO")
    print(SEPARADOR)
    print("  1 - Leitor")
    print("  2 - Bibliotecario")
    opcao = ler_inteiro("  Tipo: ", 1, 2)

    nome = ler_texto("  Nome: ")
    cpf = ler_texto("  CPF (somente digitos): ")
    email = ler_texto("  E-mail: ")

    try:
        buscar_usuario(cpf)
        raise EntradaInvalidaError("Ja existe um usuario cadastrado com este CPF.")
    except UsuarioNaoEncontradoError:
        pass

    senha = ler_texto("  Senha (minimo 4 caracteres): ")
    aceita_lgpd = ler_confirmacao("  Autoriza o uso dos seus dados (LGPD)?")

    if opcao == 1:
        data_nascimento = ler_texto("  Data de nascimento (dd/mm/aaaa): ")
        limite = ler_inteiro("  Maximo de emprestimos simultaneos: ", 1)
        novo = Leitor(nome, cpf, email, data_nascimento, limite)
    else:
        matricula = ler_texto("  Matricula funcional: ")
        setor = ler_texto("  Setor: ")
        novo = Bibliotecario(nome, cpf, email, matricula, setor)

    novo.definir_senha(senha)
    novo.aceitar_consentimento(aceita_lgpd)

    usuarios.append(novo)
    salvar_dados()
    lgpd.registrar_log("Cadastro de usuario", novo.cpf, f"{novo.tipo()}: {novo.nome}")
    print(f"\n  [OK] {novo.tipo()} '{novo.nome}' cadastrado (ID {novo.id}).")
    print(f"  [LGPD] Senha armazenada como SHA-256: {novo.senha_hash[:16]}...")
    print(f"  [LGPD] Consentimento registrado: {'SIM' if aceita_lgpd else 'NAO'}")

# RF02 - Cadastro de materiais
def op_cadastrar_material() -> None:
    print(SEPARADOR)
    print("  RF02 - CADASTRO DE MATERIAL")
    print(SEPARADOR)
    print("  1 - Livro Fisico")
    print("  2 - Livro Digital")
    print("  3 - Revista")
    opcao = ler_inteiro("  Tipo: ", 1, 3)

    titulo = ler_texto("  Titulo: ")
    autor = "N/A" if opcao == 3 else ler_texto("  Autor: ")
    exemplares = ler_inteiro("  Quantidade de exemplares: ", 1)

    from .modelos.livro_digital import LivroDigital
    from .modelos.livro_fisico import LivroFisico
    from .modelos.revista import Revista

    if opcao == 1:
        isbn = ler_texto("  ISBN: ")
        material = LivroFisico(isbn, titulo, autor, exemplares)
    elif opcao == 2:
        isbn = ler_texto("  ISBN: ")
        tamanho = ler_texto("  Tamanho do arquivo (MB): ")
        formato = ler_texto("  Formato (PDF, EPUB, MOBI...): ")
        material = LivroDigital(isbn, titulo, autor, tamanho, formato)
    else:
        issn = ler_texto("  ISSN: ")
        edicao = ler_texto("  Edicao: ")
        material = Revista(issn, titulo, edicao, autor, exemplares)

    materiais.append(material)
    salvar_dados()
    lgpd.registrar_log("Cadastro de material", "-", f"{material.tipo()}: {titulo}")
    print(f"\n  [OK] {material.tipo()} '{titulo}' cadastrado (ID {material.id}).")

# RF03 - Emprestimo
def op_realizar_emprestimo() -> None:
    print(SEPARADOR)
    print("  RF03 - REALIZAR EMPRESTIMO")
    print(SEPARADOR)

    cpf = ler_texto("  CPF do usuario: ")
    usuario = buscar_usuario(cpf)
    id_material = ler_inteiro("  ID do material: ", 1)
    material = buscar_material(id_material)

    reserva = (usuario.cpf, material.id)
    primeiro_da_fila = bool(fila_reservas) and fila_reservas[0] == reserva
    segurado = material.exemplares_reservados > 0

    if segurado and not primeiro_da_fila:
        raise MaterialIndisponivelError(
            f"'{material.titulo}' tem exemplar segurado para outro usuario "
            "da fila de reserva."
        )
    if not segurado and material.exemplares_disponiveis <= 0:
        raise MaterialIndisponivelError(
            f"'{material.titulo}' nao tem exemplares disponiveis. "
            "Use a opcao 5 para entrar na fila de espera."
        )

    ativos = emprestimos_ativos_do(usuario.cpf)
    if isinstance(usuario, Leitor) and len(ativos) >= usuario.limite_emprestimos:
        raise LimiteEmprestimosError(
            f"{usuario.nome} atingiu o limite de "
            f"{usuario.limite_emprestimos} emprestimos simultaneos."
        )

    novo = Emprestimo(
        id_emprestimo=proximo_id_emprestimo(),
        id_usuario=usuario.id,
        cpf_usuario=usuario.cpf,
        id_material=material.id,
    )
    emprestimos.append(novo)
    historico_emprestimos.setdefault(usuario.cpf, []).append(novo.id)

    if segurado:
        material.atender_reserva()
    else:
        material.remover_disponivel(1)
    material.registrar_emprestimo()

    if reserva in fila_reservas:
        fila_reservas.remove(reserva)

    salvar_dados()
    lgpd.registrar_log(
        "Emprestimo", usuario.cpf,
        f"Material {material.id} - {material.titulo}",
    )

    print(f"\n  [OK] Emprestimo #{novo.id} registrado para {usuario.nome}.")
    print(f"  Material ......... {material.titulo}")
    print(f"  Data emprestimo .. {novo.data_emprestimo}")
    print(f"  Devolucao prevista {novo.data_prevista}")
    print(f"  Disponiveis agora . {material.exemplares_disponiveis}")

# RF04 - Reserva (fila de espera)
def op_reservar_material() -> None:
    print(SEPARADOR)
    print("  RF04 - RESERVAR MATERIAL (fila de espera)")
    print(SEPARADOR)

    cpf = ler_texto("  CPF do usuario: ")
    usuario = buscar_usuario(cpf)
    id_material = ler_inteiro("  ID do material: ", 1)
    material = buscar_material(id_material)

    if material.exemplares_disponiveis > 0:
        raise EntradaInvalidaError(
            "Existem exemplares disponiveis - use a opcao 3 (emprestimo)."
        )

    reserva = (usuario.cpf, material.id)
    if reserva in fila_reservas:
        raise ReservaJaRealizadaError(
            f"{usuario.nome} ja esta na fila de '{material.titulo}'."
        )

    fila_reservas.append(reserva)
    salvar_dados()
    lgpd.registrar_log(
        "Reserva", usuario.cpf, f"Material {material.id} - {material.titulo}"
    )

    posicao = list(fila_reservas).index(reserva) + 1
    print(f"\n  [OK] {usuario.nome} entrou na fila de '{material.titulo}'.")
    print(f"  Posicao na fila: {posicao} de {len(fila_reservas)}")

# Devolucao + multa polimorfica + atendimento da fila
def op_realizar_devolucao() -> None:
    print(SEPARADOR)
    print("  DEVOLUCAO DE MATERIAL")
    print(SEPARADOR)

    cpf = ler_texto("  CPF do usuario: ")
    usuario = buscar_usuario(cpf)
    ativos = emprestimos_ativos_do(usuario.cpf)

    if not ativos:
        raise EmprestimoNaoEncontradoError(
            f"{usuario.nome} nao possui emprestimos ativos."
        )

    print("  Emprestimos ativos:")
    for emprestimo in ativos:
        material = buscar_material(emprestimo.id_material)
        print(f"    #{emprestimo.id} - {material.titulo} "
              f"(prevista: {emprestimo.data_prevista})")

    id_escolhido = ler_inteiro("  ID do emprestimo a devolver: ", 1)
    emprestimo = next((e for e in ativos if e.id == id_escolhido), None)
    if emprestimo is None:
        raise EmprestimoNaoEncontradoError(
            "Emprestimo nao encontrado entre os ativos deste usuario."
        )

    material = buscar_material(emprestimo.id_material)
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    dias = emprestimo.dias_atraso(data_hoje)

    multa = material.calcular_multa(dias)
    emprestimo.registrar_devolucao(multa)

    reserva_atendida = next(
        (r for r in fila_reservas if r[1] == material.id), None
    )
    if reserva_atendida:
        material.segregar_para_reserva()
    else:
        material.adicionar_disponivel(1)

    salvar_dados()
    lgpd.registrar_log(
        "Devolucao", usuario.cpf,
        f"Material {material.id} - {material.titulo}",
    )

    print(f"\n  [OK] Devolucao de '{material.titulo}' registrada em {data_hoje}.")
    if dias > 0:
        print(f"  Atraso ........... {dias} dia(s)")
        print(f"  Multa ({material.tipo()}) ... R$ {multa:.2f}")
    else:
        print("  Dentro do prazo - sem multa.")
    print(f"  Disponiveis agora . {material.exemplares_disponiveis}"
          f" (reservados: {material.exemplares_reservados})")

    if reserva_atendida:
        cpf_reserva, _ = reserva_atendida
        try:
            nome_reservante = buscar_usuario(cpf_reserva).nome
        except UsuarioNaoEncontradoError:
            nome_reservante = cpf_reserva
        print(f"  [FILA] Exemplar SEGURADO para {nome_reservante} "
              "- faca o emprestimo (opcao 3); a reserva so sai da fila "
              "nesse momento.")

# RF05 - Avaliacao
def op_avaliar_material() -> None:
    print(SEPARADOR)
    print("  RF05 - AVALIAR MATERIAL (somente apos devolucao)")
    print(SEPARADOR)

    cpf = ler_texto("  CPF do usuario: ")
    usuario = buscar_usuario(cpf)
    id_material = ler_inteiro("  ID do material: ", 1)
    material = buscar_material(id_material)

    if not usuario_devolveu(usuario.cpf, material.id):
        raise AvaliacaoInvalidaError(
            f"{usuario.nome} ainda nao devolveu '{material.titulo}'. "
            "A avaliacao e liberada apos a devolucao."
        )

    nota = ler_inteiro("  Nota (1 a 5): ", 1, 5)
    comentario = input("  Comentario (opcional): ").strip()

    material.avaliar(nota, comentario)
    avaliacoes.append({
        "usuario": usuario.cpf,
        "nome_usuario": usuario.nome,
        "id_material": material.id,
        "titulo": material.titulo,
        "nota": nota,
        "comentario": comentario,
        "data": datetime.now().strftime("%d/%m/%Y"),
    })

    salvar_dados()
    lgpd.registrar_log(
        "Avaliacao", usuario.cpf,
        f"Material {material.id} - nota {nota}",
    )

    print(f"\n  [OK] Avaliacao registrada para '{material.titulo}'.")
    print(f"  Media atual ....... {material.calcular_media():.2f}")
    print(f"  Total avaliacoes .. {material.total_avaliacoes}")

# Consulta de materiais
def op_consultar_materiais() -> None:
    print(SEPARADOR)
    print("  CONSULTA DE MATERIAIS")
    print(SEPARADOR)

    if not materiais:
        print("  Nenhum material cadastrado.")
        return

    busca = input("  Buscar por titulo (vazio = listar todos): ").strip().lower()
    encontrados = [m for m in materiais if not busca or busca in m.titulo.lower()]

    if not encontrados:
        print("  Nenhum material encontrado.")
        return

    for material in encontrados:
        print(SEPARADOR)
        print(f"  ID {material.id} | {material.tipo()} | {material.titulo}")
        print(f"    Autor ......... {material.autor}")
        print(f"    Exemplares .... {material.exemplares_disponiveis}/"
              f"{material.total_exemplares} disponiveis")
        if material.exemplares_reservados:
            print(f"    Reservados .... {material.exemplares_reservados} "
                  "(segurados para a fila)")
        print(f"    Emprestimos ... {material.total_emprestimos}")
        print(f"    Avaliacoes .... {material.calcular_media():.2f} "
              f"({material.total_avaliacoes} nota(s))")
        for chave, valor in material.dados_especificos().items():
            print(f"    {chave.capitalize()} ... {valor}")

# Consulta de usuarios
def op_consultar_usuarios() -> None:
    print(SEPARADOR)
    print("  CONSULTA DE USUARIOS")
    print(SEPARADOR)

    if not usuarios:
        print("  Nenhum usuario cadastrado.")
        return

    for usuario in usuarios:
        ativos = emprestimos_ativos_do(usuario.cpf)
        print(SEPARADOR)
        print(f"  ID {usuario.id} | {usuario.tipo()} | {usuario.nome}")
        print(f"    CPF ........... {usuario.cpf}")
        print(f"    E-mail ........ {usuario.email}")
        for campo, valor in usuario.dados_especificos().items():
            print(f"    {campo.replace('_', ' ').capitalize()} ... {valor}")
        print(f"    Emprestimos ativos: {len(ativos)}")
        print(f"    Consentimento LGPD: "
              f"{'SIM' if usuario.consentimento.get('aceito') else 'NAO'}")

    print(SEPARADOR)
    if ler_confirmacao("  Deseja anonimizar algum usuario (LGPD)?"):
        cpf = ler_texto("  CPF do usuario a anonimizar: ")
        usuario = buscar_usuario(cpf)
        if not ler_confirmacao(f"  Confirmar anonimizacao de '{usuario.nome}'?"):
            print("  Operacao cancelada.")
            return
        lgpd.anonimizar_usuario(usuario)
        salvar_dados()
        lgpd.registrar_log("Anonimizacao de usuario", cpf,
                           "Dados pessoais removidos")
        print(f"  [OK] Usuario {usuario.id} anonimizado com sucesso.")

# Relatorio de emprestimos
def op_relatorio_emprestimos() -> None:
    print(SEPARADOR)
    print("  RELATORIO DE EMPRESTIMOS")
    print(SEPARADOR)

    if not emprestimos:
        print("  Nenhum emprestimo registrado.")
        return

    ativos = [e for e in emprestimos if e.ativo]
    devolvidos = [e for e in emprestimos if not e.ativo]
    em_atraso = [e for e in ativos if e.dias_atraso() > 0]
    total_multas = sum(e.multa for e in devolvidos)

    print(f"  Total de emprestimos ...... {len(emprestimos)}")
    print(f"  Ativos .................... {len(ativos)}")
    print(f"  Devolvidos ................ {len(devolvidos)}")
    print(f"  Em atraso (hoje) .......... {len(em_atraso)}")
    print(f"  Arrecadado em multas ...... R$ {total_multas:.2f}")
    print(f"  Usuarios com historico .... {len(historico_emprestimos)}")

    print("\n  Historico por usuario (dicionario historico_emprestimos):")
    for cpf, ids in historico_emprestimos.items():
        try:
            nome = buscar_usuario(cpf).nome
        except UsuarioNaoEncontradoError:
            nome = "(anonimizado)"
        print(f"    {cpf} -> {nome}: emprestimos {ids}")

    print("\n  Detalhamento:")
    for emprestimo in emprestimos:
        material = buscar_material(emprestimo.id_material)
        situacao = ("ATIVO" if emprestimo.ativo
                    else f"devolvido {emprestimo.data_devolucao}")
        print(f"    #{emprestimo.id} | {material.titulo} | "
              f"{emprestimo.cpf_usuario} | {situacao} | "
              f"multa R$ {emprestimo.multa:.2f}")

# RF06 - Recomendacoes
def op_recomendacoes() -> None:
    print(SEPARADOR)
    print("  RF06 - RECOMENDACOES AUTOMATICAS")
    print(SEPARADOR)

    if not materiais:
        print("  Nenhum material cadastrado.")
        return

    avaliados = [m for m in materiais if m.total_avaliacoes > 0]
    por_media = sorted(avaliados, key=lambda m: m.calcular_media(), reverse=True)

    print("  TOP por MAIOR MEDIA de avaliacoes:")
    if not por_media:
        print("    Nenhum material foi avaliado ainda.")
    for i, material in enumerate(por_media[:5], start=1):
        print(f"    {i}o. {material.titulo} - media "
              f"{material.calcular_media():.2f} "
              f"({material.total_avaliacoes} nota(s))")

    por_emprestimos = sorted(
        materiais, key=lambda m: m.total_emprestimos, reverse=True
    )
    print("\n  TOP por MAIOR NUMERO de emprestimos:")
    for i, material in enumerate(por_emprestimos[:5], start=1):
        print(f"    {i}o. {material.titulo} - {material.total_emprestimos} "
              "emprestimo(s)")

# Desafio extra - LGPD
def op_relatorio_lgpd() -> None:
    """Gera o relatorio de acessibilidade e uso da plataforma."""
    relatorio = lgpd.gerar_relatorio_uso(usuarios, materiais, emprestimos)
    print()
    print(lgpd.formatar_relatorio_uso(relatorio))
    lgpd.registrar_log("Relatorio de uso", "-", "Relatorio LGPD gerado")

# Menu principal
def _exibir_menu() -> None:
    print(SEPARADOR)
    print("  BIBLIOTECA DIGITAL COMUNITARIA - MENU PRINCIPAL")
    print(SEPARADOR)
    print("   1 - Cadastrar usuario")
    print("   2 - Cadastrar material")
    print("   3 - Realizar emprestimo")
    print("   4 - Realizar devolucao")
    print("   5 - Reservar material")
    print("   6 - Avaliar material")
    print("   7 - Consultar materiais")
    print("   8 - Consultar usuarios")
    print("   9 - Relatorio de emprestimos")
    print("  10 - Recomendacoes")
    print("  11 - Relatorio de uso (LGPD)")
    print("   0 - Sair")
    print(SEPARADOR)

def executar() -> None:
    """Carrega os dados e mantem o loop do menu ativo."""
    carregar_dados()
    lgpd.registrar_log("Sistema iniciado", "-", "Menu principal")
    print("\n  Dados carregados: "
          f"{len(usuarios)} usuario(s), {len(materiais)} material(is), "
          f"{len(emprestimos)} emprestimo(s).")

    acoes = {
        1: op_cadastrar_usuario,
        2: op_cadastrar_material,
        3: op_realizar_emprestimo,
        4: op_realizar_devolucao,
        5: op_reservar_material,
        6: op_avaliar_material,
        7: op_consultar_materiais,
        8: op_consultar_usuarios,
        9: op_relatorio_emprestimos,
        10: op_recomendacoes,
        11: op_relatorio_lgpd,
    }

    while True:
        print()
        _exibir_menu()
        opcao = ler_inteiro("  Escolha uma opcao: ", 0, 11)

        if opcao == 0:
            salvar_dados()
            lgpd.registrar_log("Sistema encerrado", "-", "Opcao 0")
            print("\n  Dados salvos. Ate logo!")
            break

        try:
            acoes[opcao]()
        except (EntradaInvalidaError, UsuarioNaoEncontradoError,
                MaterialNaoEncontradoError, MaterialIndisponivelError,
                LimiteEmprestimosError, AvaliacaoInvalidaError,
                ReservaJaRealizadaError, EmprestimoNaoEncontradoError,
                ValueError) as erro:
            print(f"\n  [ERRO] {erro}")
        except Exception as erro:
            print(f"\n  [ERRO INESPERADO] {erro}")
