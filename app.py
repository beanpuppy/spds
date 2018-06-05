import re
from multiprocessing.dummy import Pool as ThreadPool
from flask import Flask, request, redirect, g, render_template, session, jsonify
from playhouse.shortcuts import model_to_dict, dict_to_model

from api import spotify, genius
from config import Config
from models.main import *

app = Flask(__name__)
app.secret_key = 'some key for session'
AUTH_HEADER = ''

"""AUTH STUFF"""

@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)

@app.route("/callback/")
def callback():
    auth_token  = request.args['code']
    auth_header = spotify.authorise(auth_token)
    session['auth_header'] = auth_header

    return redirect("/search", code=302)

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

@app.route('/score')
def score():
    if 'auth_header' not in session: return search()

    return render_template('score.html')

def score_track(track):
    query = Track.select().where(Track.spotify_id == track['track']['id'])
    if query.exists(): return {**track, **model_to_dict(query[0])}

    lyrics, genius_id = genius.get_lyrics(track['track']['name'], track['track']['artists'][0]['name'])

    audio           = spotify.get_audio_features(track['track']['id'])
    audio_valence   = audio['valence']
    lyrical_valence = 0
    score           = round(audio_valence * 100)
    incomplete      = 'yes'

    if 'error' not in lyrics:
        words = re.split(r'[\s\]\[]', lyrics)
        for word in words:
            if word in Config.LEXICON_SADNESS: lyrical_valence += 1
            if word in Config.LEXICON_FEAR: lyrical_valence += 0.5
            if word in Config.LEXICON_ANGER: lyrical_valence += 0.25

        percent_sad     = lyrical_valence / len(words) * 100
        lyrical_density = len(words) / track['track']['duration_ms'] * 1000
        score           = round(1 - (1 - audio_valence) + (percent_sad * (1 + lyrical_density))) / 2
        incomplete      = 'no'

    Track.insert(
        spotify_id = track['track']['id'],
        genius_id = genius_id,
        name = track['track']['name'],
        score = score,
        incomplete = incomplete
    ).execute()

    return {**track, 'lyrics': lyrical_valence, 'audio': audio_valence, 'score': score, 'incomplete': incomplete}

def get_stats(analysis):
    pass

@app.route('/analyse', methods=['GET'])
def analyse():
    if 'auth_header' not in session: return {'error':{'status':'440', 'message':'Not authenticated'}}
    auth_header = session['auth_header']
    user        = spotify.get_users_profile(auth_header)

    playlist_id = request.args.get('playlist')
    playlist    = spotify.get_playlist(user.get('id'), playlist_id, auth_header)
    owner       = playlist['owner']['display_name'] or playlist['owner']['id']
    tracks      = spotify.get_playlist_tracks(user.get('id'), playlist_id, auth_header)

    pool     = ThreadPool(8)
    analysis = pool.map(score_track, tracks)

    playlist_valence = 0
    for track in analysis: playlist_valence += track['score']
    score = round(playlist_valence / len(analysis))

    Playlist.replace(
        playlist_id = playlist_id,
        name = playlist['name'],
        author = owner,
        date = fn.Now(),
        score = score
    ).execute()

    return jsonify({**playlist, 'score': score, 'tracks': analysis})

if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)
