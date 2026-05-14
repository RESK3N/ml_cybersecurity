import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import Flask, redirect
from flask_login import LoginManager, logout_user

from auth import User

server = Flask(__name__)
server.secret_key = 'super-secret-key-for-secure-dashboard'

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

@login_manager.user_loader
def load_user(username):
    return User(username)

# Initialize Dash
app = dash.Dash(
    __name__, 
    server=server, 
    use_pages=True, 
    external_stylesheets=[
        dbc.themes.CYBORG, 
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
    ],
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    dash.page_container
])

@server.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
