from dash import Dash
import dash_bootstrap_components as dbc
import time

from game_state import game_state_manager
from layout import create_layout
from callbacks import register_callbacks
from websocket_server import WebSocketServer

ws_server = WebSocketServer(game_state_manager, host="0.0.0.0", port=8765)
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Auction Game Dashboard"
app.layout = create_layout()
register_callbacks(app, game_state_manager, ws_server)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Auction Game Dashboard")
    print("=" * 60)
    ws_server.run_in_thread()
    time.sleep(1)
    print(f"✓ WebSocket: ws://0.0.0.0:8765")
    print(f"✓ Dashboard: http://0.0.0.0:8050")
    print("=" * 60)
    app.run(host="0.0.0.0", port=8050, debug=False)
