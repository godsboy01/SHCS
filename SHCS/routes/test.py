import asyncio
import websockets

async def test_websocket():
    async with websockets.connect('ws://127.0.0.1:5000') as websocket:
        # 发送消息
        await websocket.send('Hello, WebSocket!')

        # 接收消息
        response = await websocket.recv()
        print(f'收到消息: {response}')

# 运行测试
asyncio.get_event_loop().run_until_complete(test_websocket())