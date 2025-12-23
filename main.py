# ./main.py
import asyncio
import sys
from telethon import TelegramClient, events
from config import config, app_shortname, get_db_config
from config.postgres_session import PostgresSession
from config.postgres_events import PostgresEvents
from telethon.errors import RPCError
from telethon.tl.types import UpdatesTooLong
import config.libs as libs
from config.db import DB_CONFIG


async def main():
    try:
        db_config_validated = get_db_config()
        print(f"{libs.horaagora()} - ✅ db_config validado!")
    except Exception as e:
        print(f"{libs.horaagora()} - ❌ Erro ao obter DB_CONFIG validado: {e}")
        print(f"{libs.horaagora()} -    Tentando usar DB_CONFIG global...")
        db_config_validated = DB_CONFIG.copy() if isinstance(DB_CONFIG, dict) else {}
        if 'host' not in db_config_validated or not db_config_validated.get('host'):
            raise ValueError(f"{libs.horaagora()} - ❌ Não foi possível obter uma configuração de banco de dados válida!")

    session = PostgresSession(config["session"], db_config_validated)
    eventos = PostgresEvents(config["session"], db_config_validated)
    client = TelegramClient(session, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"], password=config["phpass"])

    @client.on(events.Raw)
    async def handle_raw_event(event):
        if isinstance(event, UpdatesTooLong):
            print(f"{libs.horaagora()} - Conexão perdida. Tentando reconectar...")
        else:
            tipo_evento = type(event).__name__
            if tipo_evento == 'UpdateNewChannelMessage':
                msg_tipo_evento = f"{libs.GREEN}{tipo_evento}{libs.ENDC}"
            elif tipo_evento == 'UpdateDeleteChannelMessages':
                msg_tipo_evento = f"{libs.RED}{tipo_evento}{libs.ENDC}"
            elif tipo_evento == 'UpdateReadChannelInbox':
                msg_tipo_evento = f"{libs.LIGHTBLUE}{tipo_evento}{libs.ENDC}"
            elif tipo_evento == 'UpdateUserStatus':
                msg_tipo_evento = f"{libs.ORANGE_BOLD}{tipo_evento}{libs.ENDC}"
            elif tipo_evento == 'UpdateChannelUserTyping':
                msg_tipo_evento = f"{libs.LIGHT_CYAN}{tipo_evento}{libs.ENDC}"
            elif tipo_evento == 'UpdateEditChannelMessage':
                msg_tipo_evento = f"{libs.YELLOW_BOLD}{tipo_evento}{libs.ENDC}"
            else:
                msg_tipo_evento = tipo_evento
            # print(f"{libs.horaagora()} -  Evento recebido: {msg_tipo_evento}")


            eventos.save_type_event(tipo_evento)
            event_data = {
                    'type': tipo_evento,
                    'date': getattr(event, 'date', None),
                    'message': getattr(getattr(event, 'message', None), 'id', None),
                    'raw_data': event.to_dict() if hasattr(event, 'to_dict') else str(event)
                }
            eventos.save_event(event_data)


    await client.send_message('me', f"Logado como: {app_shortname}")
    print(f"{libs.horaagora()} - {libs.DARK_GREY} Iniciado e aguardando mensagens...{libs.ENDC}")

    await client.run_until_disconnected()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print(f"{libs.horaagora()} - Interrupção solicitado pelo usuário.")
    sys.exit(0)
except RPCError as e:
    print(f"{libs.horaagora()} - Erro na conexão com o Telegram: {e}")
except Exception as e:
    import traceback
    print(f"{libs.horaagora()} - Erro inesperado: {e}")
    print(f"{libs.horaagora()} - Tipo do erro: {type(e).__name__}")
    print(f"{libs.horaagora()} - Traceback completo:")
    traceback.print_exc()

