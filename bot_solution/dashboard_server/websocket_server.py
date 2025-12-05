import asyncio
import json
import websockets
from threading import Thread

class WebSocketServer:
    def __init__(self, state_manager, host="0.0.0.0", port=8765):
        self.state_manager = state_manager
        self.host = host
        self.port = port
        self.clients = set()
        self.client_info = {}
    
    async def handle_client(self, websocket, path):
        """Handle incoming WebSocket connections."""
        client_addr = websocket.remote_address
        self.clients.add(websocket)
        print(f"✅ Bot connected from {client_addr}. Total clients: {len(self.clients)}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    agent_id = data.get('agent_id', 'unknown')
                    round_num = data.get('round', 'N/A')
                    
                    self.client_info[websocket] = {
                        "agent_id": agent_id,
                        "last_round": round_num
                    }
                    
                    print(f"📥 Received from {agent_id}: Round {round_num}")
                    
                    # Update game state
                    self.state_manager.update(data)
                    
                    # Echo confirmation back to client
                    await websocket.send(json.dumps({
                        "status": "received",
                        "round": round_num,
                        "timestamp": data.get("timestamp")
                    }))
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON from {client_addr}: {e}")
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
                except Exception as e:
                    print(f"❌ Error processing message from {client_addr}: {e}")
                    await websocket.send(json.dumps({"error": str(e)}))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Bot disconnected: {client_addr}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            self.clients.discard(websocket)
            self.client_info.pop(websocket, None)
            print(f"📊 Remaining clients: {len(self.clients)}")
    
    async def start_server(self):
        """Start the WebSocket server."""
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"🔌 WebSocket server listening on ws://{self.host}:{self.port}")
            await asyncio.Future()
    
    def run_in_thread(self):
        """Run the WebSocket server in a separate thread."""
        def run():
            asyncio.run(self.start_server())
        
        thread = Thread(target=run, daemon=True)
        thread.start()
        return thread

