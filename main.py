# ./main.py
import asyncio
from telethon import TelegramClient, events
from config import config, db_config, app_shortname
from config.postgres_session import PostgresSession
from config.postgres_events import PostgresEvents 
from telethon.errors import RPCError
from telethon.tl.types import UpdatesTooLong

async def main():
    session = PostgresSession(config["session"], db_config)
    eventos = PostgresEvents(config["session"], db_config)
    client = TelegramClient(session, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"], password=config["phpass"])

    @client.on(events.Raw)
    async def handle_raw_event(event):
        if isinstance(event, UpdatesTooLong):
            print("Conexão perdida. Tentando reconectar...")
        else:
            tipo_evento = type(event).__name__
            print(f"Evento recebido: {tipo_evento}")
            eventos.save_type_event(tipo_evento)
            event_data = {
                    'type': tipo_evento,
                    'date': getattr(event, 'date', None),
                    'message': getattr(getattr(event, 'message', None), 'id', None),
                    'raw_data': event.to_dict() if hasattr(event, 'to_dict') else str(event)
                }
            eventos.save_event(event_data)
            # print(f"Evento recebido _")
            # print(event_data)

    await client.send_message('me', f"Logado como: {app_shortname}")
    print("Iniciado e aguardando mensagens...")

    await client.run_until_disconnected()

try:
    asyncio.run(main())
except RPCError as e:
    print(f"Erro na conexão com o Telegram: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")

