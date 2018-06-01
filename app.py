from flask import Flask, request, redirect, g, render_template, session, jsonify
from api import spotify
from models.main import *

app = Flask(__name__)
app.secret_key = 'some key for session'

"""AUTH STUFF"""

@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)

@app.route("/callback/")
def callback():

    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header

    return search()

def valid_token(resp):
    return resp is not None and not 'error' in resp

"""WEB PAGE STUFF"""

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/search')
def search():
    if 'auth_header' in session:
        auth_header = session['auth_header']

        user = spotify.get_users_profile(auth_header)

        if valid_token(user): return render_template(
            "search.html",
            user=user,
            playlists=spotify.get_users_playlists(auth_header)['items']
        )

    return render_template('search.html')

@app.route('/analyse', methods=['GET'])
def analyse():
    if 'auth_header' not in session: return {'error':{'status':'440', 'message':'Not authenticated'}}
    auth_header = session['auth_header']

    user = spotify.get_users_profile(auth_header)

    playlist = request.args.get('playlist')
    store    = request.args.get('store')

    tracks = spotify.get_playlist_tracks(user.get('id'), playlist, auth_header)

    # Do

    # Save playlist to db if they said so
    if store == 'yes':
        pass

    return jsonify(tracks)

if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)
