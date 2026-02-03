"""
PsicoVoz - Teste de WebSocket
Executa: python test_websocket.py
"""
import asyncio
import websockets
import json

async def test_conversation():
    uri = "ws://localhost:8000/ws/voice/psicanalise"
    
    print("🔌 Conectando ao PsicoVoz...")
    
    async with websockets.connect(uri) as ws:
        print("✅ Conectado!")
        
        # Aguardar mensagem de boas-vindas
        response = await ws.recv()
        data = json.loads(response)
        print(f"\n🤖 Terapeuta: {data.get('text', '')[:200]}...")
        
        # Enviar mensagem de teste
        test_message = {
            "command": "text_message",
            "text": "Ola, estou me sentindo ansioso hoje"
        }
        
        print(f"\n👤 Voce: {test_message['text']}")
        await ws.send(json.dumps(test_message))
        
        # Aguardar resposta
        response = await ws.recv()
        data = json.loads(response)
        print(f"\n🤖 Terapeuta: {data.get('text', '')}")
        
        print("\n✅ Teste concluido com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_conversation())
