# ./config/libs.py
from datetime import datetime

# Estilo: \(0\) (normal), \(1\) (negrito), \(4\) (sublinhado).
# Cor do texto: \(30\) (branco), \(31\) (vermelho), \(32\) (verde), \(33\) (amarelo), \(34\) (azul), \(35\) (magenta), \(36\) (ciano), \(37\) (cinza).
# Cor de fundo: \(40\) (branco), \(41\) (vermelho), \(42\) (verde), \(43\) (amarelo), \(44\) (azul), \(45\) (magenta), \(46\) (ciano), \(47\) (cinza).
# print("\033[1;31mTexto em vermelho negrito\033[0m")

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW_BOLD = '\033[1;33m'
LIGHT_CYAN = '\033[0;96m'
CYAN_BOLD = '\033[1;36m'
LIGHTBLUE = '\033[0;94m'
ORANGE_BOLD = '\033[1;33m'
DARK_GREY = '\033[0;90m'
ENDC = '\033[0m' # Reset color

def horaagora(printc: bool = False):
    content = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    if printc:
        print(content)
    return content
