"""Sistema Inteligente de Biblioteca Digital Comunitaria - main.py.

Executa com: python -m biblioteca.main
"""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from biblioteca.menu import executar
else:
    from .menu import executar


def main() -> None:
    """Inicializa o menu principal do sistema."""
    print("=" * 58)
    print("  SISTEMA INTELIGENTE DE BIBLIOTECA DIGITAL COMUNITARIA")
    print("  Prefeitura Municipal - Incentivo a leitura e ao conhecimento")
    print("=" * 58)
    executar()


if __name__ == "__main__":
    main()
