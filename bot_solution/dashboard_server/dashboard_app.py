from dash import Dash
import dash_bootstrap_components as dbc

# Import modular components
from game_state import game_state_manager
from layout import create_layout
from callbacks import register_callbacks

# Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Auction Game Dashboard"

# Set layout
app.layout = create_layout()

# Register callbacks
register_callbacks(app, game_state_manager)

def update_game_data(data: dict):
    """
    Public API for updating game data from external sources.
    Call this from your FastAPI server to push updates.
    """
    game_state_manager.update(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)