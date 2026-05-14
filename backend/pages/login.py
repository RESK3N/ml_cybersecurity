import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import login_user, current_user
from auth import User, authenticate_user

# Register page
dash.register_page(__name__, path='/login', name="Network Admin Login")

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.I(className="bi bi-shield-lock-fill", style={"fontSize": "3rem", "color": "#00f2fe"}),
                                        html.H2("Admin Access", className="text-center mb-4 mt-2", style={"color": "white"}),
                                    ],
                                    className="text-center"
                                ),
                                html.Div(id="login-alert", style={"marginTop": "10px"}),
                                dbc.Form(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Label("Username", width=12, style={"color": "#a0aab2"}),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type="text", id="login-username", placeholder="Enter LDAP username (e.g. tesla)",
                                                        className="custom-input"
                                                    ),
                                                    width=12,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Password", width=12, style={"color": "#a0aab2"}),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type="password", id="login-password", placeholder="Enter password",
                                                        className="custom-input"
                                                    ),
                                                    width=12,
                                                ),
                                            ],
                                            className="mb-4",
                                        ),
                                        dbc.Button(
                                            "Secure Login", color="primary", id="login-button", n_clicks=0, className="w-100 fw-bold custom-btn"
                                        ),
                                    ]
                                ),
                                dcc.Location(id='login-url', refresh=True),
                            ]
                        )
                    ],
                    className="glass-card shadow-lg p-3",
                    style={"borderRadius": "15px", "border": "1px solid rgba(255,255,255,0.1)", "backgroundColor": "rgba(20,25,30,0.7)"}
                ),
                width=10,
                md=6,
                lg=4,
            ),
            className="justify-content-center align-items-center",
            style={"minHeight": "100vh"}
        )
    ],
    fluid=True,
    className="login-bg"
)

@callback(
    Output("login-url", "pathname"),
    Output("login-alert", "children"),
    Input("login-button", "n_clicks"),
    State("login-username", "value"),
    State("login-password", "value"),
    prevent_initial_call=True
)
def login_auth(n_clicks, username, password):
    if n_clicks > 0:
        if authenticate_user(username, password):
            user = User(username)
            login_user(user)
            return "/", ""
        else:
            return dash.no_update, dbc.Alert("Invalid Credentials or LDAP Error", color="danger", duration=4000)
    return dash.no_update, dash.no_update
