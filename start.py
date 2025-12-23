#!/usr/bin/env python3
"""
Script de inicialização para produção.
Inicia o cliente Telegram e a GUI Flask em processos separados.
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from config import libs

# Adiciona o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

def check_env():
    """Verifica se as variáveis de ambiente necessárias estão definidas."""
    required_vars = [
        'APP_IP', 'API_HASH', 'SESSION_NAME', 'PHONE_NUMBER',
        'DB_CONFIG_DBNAME', 'DB_CONFIG_USER', 'DB_CONFIG_PASSWORD',
        'DB_CONFIG_HOST', 'DB_CONFIG_PORT'
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"{libs.horaagora()} - ❌ Variáveis de ambiente faltando: {', '.join(missing)}")
        sys.exit(1)

    print(f"{libs.horaagora()} - ✅ Todas as variáveis de ambiente necessárias estão definidas")

def start_flask_app():
    """Inicia o servidor Flask em modo produção."""
    from gui.app import app

    # Configurações de produção
    flask_host = os.getenv('FLASK_HOST', '0.0.0.0')
    flask_port = int(os.getenv('FLASK_PORT', '5000'))
    flask_debug = os.getenv('FLASK_ENV', 'production') == 'development'

    print(f"{libs.horaagora()} - 🚀 Iniciando servidor Flask na porta {flask_port}...")

    # Para produção, usar gunicorn se disponível, senão usar Flask dev server
    if os.getenv('USE_GUNICORN', 'true').lower() == 'true':
        try:
            import gunicorn.app.wsgiapp as wsgi
            sys.argv = [
                'gunicorn',
                '--bind', f'{flask_host}:{flask_port}',
                '--workers', os.getenv('GUNICORN_WORKERS', '2'),
                '--timeout', '120',
                '--access-logfile', '-',
                '--error-logfile', '-',
                'gui.app:app'
            ]
            wsgi.run()
        except ImportError:
            print(f"{libs.horaagora()} - ⚠️  Gunicorn não disponível, usando servidor Flask de desenvolvimento")
            app.run(host=flask_host, port=flask_port, debug=flask_debug)
    else:
        app.run(host=flask_host, port=flask_port, debug=flask_debug)

def start_telegram_client():
    """Inicia o cliente Telegram."""
    import asyncio
    from main import main as telegram_main

    print(f"{libs.horaagora()} - 🚀 Iniciando cliente Telegram...")

    try:
        asyncio.run(telegram_main())
    except KeyboardInterrupt:
        print(f"\n{libs.horaagora()} - ⏹️  Cliente Telegram interrompido")
    except Exception as e:
        print(f"{libs.horaagora()} - ❌ Erro no cliente Telegram: {e}")
        sys.exit(1)

def start_all():
    """Inicia ambos os serviços."""
    import multiprocessing

    check_env()

    print("=" * 60)
    print(f"{libs.horaagora()} - Iniciando serviços do Client Telegram")
    print("=" * 60)

    # Cria processos
    processes = []

    # Processo para Flask
    flask_process = multiprocessing.Process(target=start_flask_app, name='Flask')
    flask_process.daemon = True
    flask_process.start()
    processes.append(flask_process)

    # Aguarda Flask inicializar
    time.sleep(2)

    # Processo para Telegram Client (processo principal)
    telegram_process = multiprocessing.Process(target=start_telegram_client, name='Telegram')
    telegram_process.daemon = False
    telegram_process.start()
    processes.append(telegram_process)

    # Handler para sinal de interrupção
    def signal_handler(sig, frame):
        print(f"\n{libs.horaagora()} - ⏹️  Encerrando serviços...")
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=5)
                if p.is_alive():
                    p.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Aguarda processos
    try:
        telegram_process.join()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    mode = os.getenv('RUN_MODE', 'all').lower()

    if mode == 'gui':
        check_env()
        start_flask_app()
    elif mode == 'telegram':
        check_env()
        start_telegram_client()
    else:
        start_all()

