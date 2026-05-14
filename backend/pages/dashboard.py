import dash
from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from flask_login import current_user
import pandas as pd
import joblib
from datetime import datetime
import os

dash.register_page(__name__, path='/', name="Live Network Traffic")

# =========================
# LOAD MODELS & DATA
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))
if os.path.basename(BASE_DIR) != 'backend':
    # Fallback to current dir if run from backend
    BASE_DIR = os.path.abspath(os.curdir)

try:
    model = joblib.load(os.path.join(BASE_DIR, "ids_pipeline.pkl"))
    feature_columns = joblib.load(os.path.join(BASE_DIR, "feature_columns.pkl"))
    traffic_data = pd.read_csv(os.path.join(BASE_DIR, "live_attack.csv"))
except Exception as e:
    print(f"Warning: Could not load models or data. Ensure you are running from backend dir. Error: {e}")
    model = None
    feature_columns = []
    traffic_data = pd.DataFrame()

global_traffic_index = 0
MAX_HISTORY = 30

# Initialize global state for graph history
history = {
    'timestamps': [],
    'probabilities': [],
    'labels': [],
    'severities': [],
    'predictions': []
}

def require_login(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return html.Div([
                dcc.Location(id='redirect-login', pathname='/login', refresh=True)
            ])
        return func(*args, **kwargs)
    return wrapper

@require_login
def layout():
    return dbc.Container(
        [
            dcc.Interval(id='live-update-interval', interval=2000, n_intervals=0), # 2 seconds
            
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.H2("NOC Dashboard", className="fw-bold text-white m-0"),
                            html.P("Live Intrusion Detection System", className="text-muted m-0")
                        ]),
                        width=8
                    ),
                    dbc.Col(
                        html.Div([
                            html.Span(f"Admin: {current_user.id}", className="me-3 text-info fw-bold"),
                            html.A("Logout", href="/logout", className="btn custom-btn btn-sm")
                        ], className="text-end mt-2"),
                        width=4
                    )
                ],
                className="mb-4 pb-3 border-bottom border-secondary align-items-center"
            ),
            
            # Main Content
            dbc.Row(
                [
                    # Left Column - Gauge & Status
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody([
                                    html.H5("Current Threat Level", className="card-title text-secondary"),
                                    dcc.Graph(id='severity-gauge', config={'displayModeBar': False}, style={'height': '250px'}),
                                    html.Div(id='latest-status', className="text-center mt-3 fs-4 fw-bold")
                                ]),
                                className="glass-card mb-4"
                            ),
                            
                            dbc.Card(
                                dbc.CardBody([
                                    html.H5("Latest Packet Info", className="card-title text-secondary"),
                                    html.Div(id='packet-details', className="mt-3 text-white small", style={"fontFamily": "monospace"})
                                ]),
                                className="glass-card"
                            )
                        ],
                        md=4
                    ),
                    
                    # Right Column - Timeline Chart
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody([
                                    html.H5("Attack Probability Timeline", className="card-title text-secondary"),
                                    dcc.Graph(id='timeline-chart', config={'displayModeBar': False}, style={'height': '400px'})
                                ]),
                                className="glass-card h-100"
                            )
                        ],
                        md=8
                    )
                ]
            ),
            
            # Log Table
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Recent Detections", className="card-title text-secondary mb-3"),
                            dbc.Table(id='log-table', striped=False, bordered=False, hover=True, className="table-dark text-white")
                        ]),
                        className="glass-card mt-4"
                    )
                )
            )
        ],
        fluid=True,
        className="p-4"
    )

@callback(
    Output('severity-gauge', 'figure'),
    Output('latest-status', 'children'),
    Output('latest-status', 'className'),
    Output('timeline-chart', 'figure'),
    Output('packet-details', 'children'),
    Output('log-table', 'children'),
    Input('live-update-interval', 'n_intervals')
)
def update_dashboard(n):
    global global_traffic_index, history
    
    if traffic_data.empty or model is None:
        return go.Figure(), "System Offline", "text-center mt-3 fs-4 fw-bold text-muted", go.Figure(), "No data available.", html.Tr()

    # Get next row
    if global_traffic_index >= len(traffic_data):
        global_traffic_index = 0
        
    row = traffic_data.iloc[global_traffic_index]
    global_traffic_index += 1
    
    sample = pd.DataFrame([row])
    
    # Process features
    X_sample = sample.drop(columns=["Destination Port", "Label", "Attack Type"], errors="ignore")
    X_sample.columns = X_sample.columns.str.strip()
    
    # Ensure exact feature order - add missing columns with 0
    for col in feature_columns:
        if col not in X_sample.columns:
            X_sample[col] = 0
            
    X_sample = X_sample[feature_columns]
    
    # Predict
    probability = model.predict_proba(X_sample)
    attack_prob = float(probability[0][1])
    
    THRESHOLD = 0.30
    prediction = 1 if attack_prob >= THRESHOLD else 0
    label = "ATTACK" if prediction == 1 else "BENIGN"
    
    if attack_prob >= 0.80:
        severity = "HIGH"
        status_color = "text-danger"
    elif attack_prob >= 0.40:
        severity = "MEDIUM"
        status_color = "text-warning"
    else:
        severity = "LOW"
        status_color = "text-success"
        
    confidence = attack_prob if prediction == 1 else (1 - attack_prob)
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Update history
    history['timestamps'].append(current_time)
    history['probabilities'].append(attack_prob)
    history['labels'].append(label)
    history['severities'].append(severity)
    history['predictions'].append(prediction)
    
    # Keep only max history
    for key in history:
        history[key] = history[key][-MAX_HISTORY:]
        
    # Create Gauge
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = attack_prob * 100,
        title = {'text': "Attack Prob %", 'font': {'color': '#a0aab2'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': "white"},
            'bar': {'color': "#00f2fe"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, 30], 'color': "rgba(0, 255, 127, 0.2)"},
                {'range': [30, 80], 'color': "rgba(255, 165, 0, 0.2)"},
                {'range': [80, 100], 'color': "rgba(255, 69, 0, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        },
        number = {'font': {'color': "white"}}
    ))
    gauge_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=10, l=10, r=10))

    # Create Timeline
    timeline_fig = go.Figure()
    
    # Color logic for markers
    colors = ['red' if l == 'ATTACK' else '#00f2fe' for l in history['labels']]
    
    timeline_fig.add_trace(go.Scatter(
        x=history['timestamps'], 
        y=[p * 100 for p in history['probabilities']],
        mode='lines+markers',
        line=dict(color='rgba(0, 242, 254, 0.5)', width=2),
        marker=dict(color=colors, size=8),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 254, 0.1)'
    ))
    timeline_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a0aab2"),
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor="rgba(255,255,255,0.1)", zeroline=False)
    )
    
    # Status Text
    status_text = f"Status: {label} ({severity})"
    status_class = f"text-center mt-3 fs-4 fw-bold {status_color}"
    
    # Packet details
    details = [
        html.Div(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")
        for k, v in list(X_sample.iloc[0].to_dict().items())[:10]
    ]
    
    # Log Table
    table_header = [html.Thead(html.Tr([html.Th("Time"), html.Th("Label"), html.Th("Severity"), html.Th("Probability")]))]
    
    rows = []
    # Show last 5 logs reversed
    for i in range(len(history['timestamps'])-1, max(-1, len(history['timestamps'])-6), -1):
        tr_class = "table-danger" if history['labels'][i] == "ATTACK" else ""
        rows.append(html.Tr([
            html.Td(history['timestamps'][i]),
            html.Td(history['labels'][i], className="fw-bold"),
            html.Td(history['severities'][i]),
            html.Td(f"{history['probabilities'][i]*100:.1f}%")
        ], className=tr_class))
        
    table_body = [html.Tbody(rows)]
    table = table_header + table_body

    return gauge_fig, status_text, status_class, timeline_fig, details, table
