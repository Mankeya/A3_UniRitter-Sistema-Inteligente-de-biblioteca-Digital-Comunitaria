# Sistema Inteligente de Biblioteca Digital Comunitária

Projeto Integrador A3 — Programação Orientada a Objetos (Python 3.12+)

Aplicação de terminal para uma prefeitura democratizar o acesso ao
conhecimento: cadastro de usuários (leitores e bibliotecários) e de
materiais (livro físico, livro digital e revista), empréstimos, reservas
em fila de espera, avaliações, recomendações automáticas e persistência
em JSON — com módulo extra de Cidadania Digital e LGPD.

## Como executar

```bash
# a partir da raiz do projeto
python -m biblioteca.main
```

Ou, no Windows, com duplo clique em `executar.bat`.

Requisitos: Python 3.12 ou superior (sem dependências externas).

## Estrutura do projeto

```
biblioteca/
├── main.py                       ponto de entrada
├── menu.py                       menu (opções 1–11 e 0) + regras RF01–RF06
├── modelos/
│   ├── pessoa.py                 Pessoa (ABC)
│   ├── leitor.py                 Leitor(Pessoa)
│   ├── bibliotecario.py          Bibliotecario(Pessoa)
│   ├── avaliavel.py              interface Avaliavel (ABC)
│   ├── material.py               Material(Avaliavel, ABC)
│   ├── livro_fisico.py           LivroFisico(Material)
│   ├── livro_digital.py          LivroDigital(Material)
│   ├── revista.py                Revista(Material)
│   └── emprestimo.py             Emprestimo
├── excecoes/
│   └── erros.py                  exceções personalizadas
├── persistencia/
│   └── json_manager.py           leitura/gravação dos JSON
├── lgpd/
│   └── cidadania_digital.py      desafio extra (+20%)
└── dados/
    ├── usuarios.json
    ├── materiais.json
    ├── emprestimos.json
    ├── avaliacoes.json
    ├── fila_reservas.json
    └── logs.json

docs/
├── diagrama_uml.md               Parte 1 — diagrama de classes (Mermaid)
└── relatorio_tecnico.md          Parte 3 — relatório técnico
```

## Requisitos funcionais cobertos

| RF | Descrição |
|---|---|
| RF01 | Cadastro de usuários (leitor e bibliotecário) |
| RF02 | Cadastro de materiais (livro físico, livro digital, revista) |
| RF03 | Empréstimo (disponibilidade, datas e baixa do exemplar) |
| RF04 | Reserva em fila de espera FIFO (persistida em JSON) |
| RF05 | Avaliação de 1 a 5 após a devolução (média e total) |
| RF06 | Recomendações por maior média e maior nº de empréstimos |

## Entregáveis

- **Parte 1** — `docs/diagrama_uml.md`
- **Parte 2** — sistema funcional em `biblioteca/`
- **Parte 3** — `docs/relatorio_tecnico.md`
- **Parte 4** — roteiro de demonstração no relatório (§12)
- **Desafio extra** — módulo de Cidadania Digital e LGPD (`biblioteca/lgpd/`)
