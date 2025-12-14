"""
Interface de administração para visualizar dados do banco de dados Telegram.
Este módulo inicia um servidor Flask web para visualização dos dados salvos.
"""
import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.app import app

if __name__ == '__main__':
    print("=" * 60)
    horaagora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"{horaagora} - Iniciando servidor de visualização do banco de dados...")
    horaagora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"{horaagora} - Acesse: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
