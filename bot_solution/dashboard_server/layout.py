from dash import html, dcc
import dash_bootstrap_components as dbc

CARD_STYLE = {
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "borderRadius": "15px",
    "padding": "20px",
    "boxShadow": "0 8px 16px rgba(0,0,0,0.3)",
    "marginBottom": "20px"
}

STAT_CARD_STYLE = {
    "background": "rgba(255, 255, 255, 0.05)",
    "backdropFilter": "blur(10px)",
    "borderRadius": "12px",
    "padding": "25px",
    "border": "1px solid rgba(255, 255, 255, 0.1)",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.2)",
    "height": "100%"
}

def create_header():
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.Span("🎲 ", style={"fontSize": "48px"}),
                    "Auction Game Dashboard"
                ], style={
                    "color": "#fff",
                    "fontWeight": "700",
                    "marginBottom": "10px",
                    "textShadow": "0 2px 10px rgba(0,0,0,0.3)"
                }),
                html.P([
                    "Real-time analytics • ",
                    html.Span(id="connection-status", style={"color": "#00ff00"})
                ], style={"color": "rgba(255,255,255,0.7)", "fontSize": "18px"})
            ], style=CARD_STYLE)
        ])
    ], className="mb-4")

def create_round_counter():
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("Current Round", style={
                    "fontSize": "16px",
                    "color": "rgba(255,255,255,0.6)",
                    "marginBottom": "10px",
                    "textTransform": "uppercase",
                    "letterSpacing": "2px"
                }),
                html.Div(id="round-display", style={
                    "fontSize": "56px",
                    "fontWeight": "800",
                    "color": "#fff",
                    "textAlign": "center"
                })
            ], style=STAT_CARD_STYLE)
        ], width=12)
    ], className="mb-4")

def create_stat_card(icon, title, value_id, color):
    return html.Div([
        html.Div(icon, style={"fontSize": "40px", "marginBottom": "10px"}),
        html.Div(title, style={
            "fontSize": "14px",
            "color": "rgba(255,255,255,0.6)",
            "marginBottom": "8px",
            "textTransform": "uppercase"
        }),
        html.Div(id=value_id, style={
            "fontSize": "36px",
            "fontWeight": "700",
            "color": color
        })
    ], style=STAT_CARD_STYLE)

def create_statistics_row():
    return dbc.Row([
        dbc.Col([create_stat_card("💰", "Mean Gold", "mean-gold", "#FFD700")], md=4, className="mb-4"),
        dbc.Col([create_stat_card("⭐", "Mean Points", "mean-points", "#00D9FF")], md=4, className="mb-4"),
        dbc.Col([create_stat_card("🏦", "Pool Gold", "pool-gold", "#FF6B6B")], md=4, className="mb-4")
    ])

def create_chart_card(chart_id):
    return html.Div([
        dcc.Graph(id=chart_id, config={'displayModeBar': False}, style={"height": "400px"})
    ], style={**STAT_CARD_STYLE, "padding": "20px"})

def create_charts_row():
    return dbc.Row([
        dbc.Col([create_chart_card("gold-distribution")], md=6, className="mb-4"),
        dbc.Col([create_chart_card("points-distribution")], md=6, className="mb-4")
    ])

def create_auctions_section():
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("🔨 Current Auctions", style={"color": "#fff", "marginBottom": "20px"}),
                html.Div(id="current-auctions-list")
            ], style=STAT_CARD_STYLE)
        ], md=6, className="mb-4"),
        dbc.Col([
            html.Div([
                html.H4("📜 Previous Results", style={"color": "#fff", "marginBottom": "20px"}),
                html.Div(id="previous-auctions-list")
            ], style=STAT_CARD_STYLE)
        ], md=6, className="mb-4")
    ])

def create_player_count():
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("👥", style={"fontSize": "30px", "marginBottom": "10px"}),
                html.Div(id="player-count", style={"fontSize": "24px", "color": "rgba(255,255,255,0.8)"})
            ], style={**STAT_CARD_STYLE, "textAlign": "center"})
        ])
    ])

def create_layout():
    return dbc.Container([
        create_header(),
        create_round_counter(),
        create_statistics_row(),
        create_charts_row(),
        create_auctions_section(),
        create_player_count(),
        dcc.Interval(id="update-interval", interval=500, n_intervals=0)
    ], fluid=True, style={"background": "#0a0e27", "minHeight": "100vh", "padding": "40px 20px"})
