from dash import Input, Output, html
import plotly.graph_objects as go
import pandas as pd

def create_histogram(df, column, color, line_color, title):
    if df.empty:
        fig = go.Figure()
    else:
        fig = go.Figure(data=[go.Histogram(
            x=df[column], nbinsx=10,
            marker=dict(color=color, line=dict(color=line_color, width=2))
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

def format_auctions_list(auctions):
    """Format auction data into HTML list"""
    if not auctions:
        return html.Div("No auctions", style={"color": "rgba(255,255,255,0.5)"})
    
    items = []
    for auction in auctions:
        items.append(html.Div([
            html.Span(f"{auction['description']}", style={"fontWeight": "bold", "color": "#FFD700"}),
            html.Span(f" → EV: {auction['expected_value']:.1f}", style={"color": "rgba(255,255,255,0.7)"})
        ], style={"marginBottom": "10px", "padding": "8px", "background": "rgba(255,255,255,0.05)", "borderRadius": "5px"}))
    
    return html.Div(items)

def format_previous_auctions_list(auctions):
    """Format previous auction results into HTML list"""
    if not auctions:
        return html.Div("No results yet", style={"color": "rgba(255,255,255,0.5)"})
    
    items = []
    for auction in auctions[:5]:  # Show last 5
        items.append(html.Div([
            html.Span(f"Winner: {auction['winning_agent']}", style={"fontWeight": "bold", "color": "#00D9FF"}),
            html.Br(),
            html.Span(f"Bid: {auction['winning_bid']} → Reward: {auction['reward']}", 
                     style={"color": "rgba(255,255,255,0.7)", "fontSize": "14px"})
        ], style={"marginBottom": "10px", "padding": "8px", "background": "rgba(255,255,255,0.05)", "borderRadius": "5px"}))
    
    return html.Div(items)

def register_callbacks(app, state_manager, ws_server):
    """Register all dashboard callbacks."""
    
    @app.callback(
        Output("round-display", "children"),
        Output("mean-gold", "children"),
        Output("mean-points", "children"),
        Output("pool-gold", "children"),
        Output("gold-distribution", "figure"),
        Output("points-distribution", "figure"),
        Output("player-count", "children"),
        Output("current-auctions-list", "children"),
        Output("previous-auctions-list", "children"),
        Input("update-interval", "n_intervals")
    )
    def update_dashboard(_):
        round_num = state_manager.get_round()
        mean_gold = state_manager.get_mean_gold()
        mean_points = state_manager.get_mean_points()
        states = state_manager.get_player_states()
        player_count = state_manager.get_player_count()
        pool = state_manager.get_pool()
        current_auctions = state_manager.get_current_auctions()
        previous_auctions = state_manager.get_previous_auctions()
        
        df = pd.DataFrame.from_dict(states, orient="index") if states else pd.DataFrame(columns=["gold", "points"])
        
        gold_fig = create_histogram(df, "gold", "#FFD700", "#FFA500", "Gold Distribution")
        points_fig = create_histogram(df, "points", "#00D9FF", "#0099CC", "Points Distribution")
        
        auctions_html = format_auctions_list(current_auctions)
        prev_auctions_html = format_previous_auctions_list(previous_auctions)
        
        return (
            f"{round_num}",
            f"{mean_gold:.2f}",
            f"{mean_points:.2f}",
            f"{pool}",
            gold_fig,
            points_fig,
            f"{player_count} Active Players",
            auctions_html,
            prev_auctions_html
        )
    
    @app.callback(
        Output("connection-status", "children"),
        Input("update-interval", "n_intervals")
    )
    def update_connection_status(_):
        """Update the WebSocket connection status."""
        num_clients = len(ws_server.clients)
        if num_clients > 0:
            return f"🟢 {num_clients} bot(s) connected"
        else:
            return "🔴 No bots connected"
