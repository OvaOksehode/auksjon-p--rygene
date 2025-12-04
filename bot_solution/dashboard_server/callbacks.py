from dash import Input, Output
import plotly.graph_objects as go
import pandas as pd

def create_histogram(df, column, color, line_color, title):
    """Create a histogram figure."""
    if df.empty:
        fig = go.Figure()
    else:
        fig = go.Figure(data=[go.Histogram(
            x=df[column],
            nbinsx=10,
            marker=dict(
                color=color,
                line=dict(color=line_color, width=2)
            )
        )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color='#fff')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.05)',
        font=dict(color='#fff'),
        xaxis=dict(title=column.capitalize(), gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title="Count", gridcolor='rgba(255,255,255,0.1)'),
        margin=dict(t=60, b=40, l=40, r=20)
    )
    return fig

def register_callbacks(app, state_manager):
    """Register all dashboard callbacks."""
    
    @app.callback(
        Output("round-display", "children"),
        Output("mean-gold", "children"),
        Output("mean-points", "children"),
        Output("gold-distribution", "figure"),
        Output("points-distribution", "figure"),
        Output("player-count", "children"),
        Input("update-interval", "n_intervals")
    )
    def update_dashboard(_):
        # Get data from state manager
        round_num = state_manager.get_round()
        mean_gold = state_manager.get_mean_gold()
        mean_points = state_manager.get_mean_points()
        states = state_manager.get_player_states()
        player_count = state_manager.get_player_count()
        
        # Create dataframe
        df = pd.DataFrame.from_dict(states, orient="index") if states else pd.DataFrame(columns=["gold", "points"])
        
        # Create charts
        gold_fig = create_histogram(df, "gold", "#FFD700", "#FFA500", "Gold Distribution")
        points_fig = create_histogram(df, "points", "#00D9FF", "#0099CC", "Points Distribution")
        
        return (
            f"{round_num}",
            f"{mean_gold:.2f}",
            f"{mean_points:.2f}",
            gold_fig,
            points_fig,
            f"{player_count} Active Players"
        )