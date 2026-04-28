import asyncio
import websockets

async def handler(websocket):
    print("Client verbonden!")

    try:
        async for message in websocket:
            print(f"Ontvangen: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client verbinding gesloten")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server draait op poort 8765...")
        await asyncio.Future()  # blijft draaien

asyncio.run(main())