import asyncio
import websockets
import json
import os
from datetime import datetime

# Simples WebSocket server para eventos de pedidos/carrinhos/notificações
clients = set()

async def notify_all(event):
    if clients:
        msg = json.dumps(event)
        await asyncio.wait([client.send(msg) for client in clients])

async def event_producer():
    # Exemplo: monitora arquivo de pedidos/notificações e envia eventos
    last_mtime = None
    path = os.path.join('out', 'report.json')
    while True:
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            if last_mtime is None:
                last_mtime = mtime
            elif mtime != last_mtime:
                with open(path, 'r', encoding='ascii') as f:
                    data = json.load(f)
                await notify_all({
                    'type': 'report_update',
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                })
                last_mtime = mtime
        await asyncio.sleep(2)

async def handler(websocket, path):
    clients.add(websocket)
    try:
        async for _ in websocket:
            pass  # Não espera mensagens do cliente
    finally:
        clients.remove(websocket)

async def main():
    server = await websockets.serve(handler, '0.0.0.0', 8765)
    await event_producer()
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
