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
    lyrical_valence = 0.9 if audio_valence > 0.3 else 0.9 - audio_valence
    score           = round(audio_valence * 100)
    incomplete      = 'yes'

    if 'error' not in lyrics:
        words = re.split(r'[\s\]\[]', lyrics)
        sad_words = 0
        for word in words:
            if word in Config.STOP_WORDS or word == '':
                words.remove(word)
                continue

            if word in Config.LEXICON_SADNESS: sad_words += 5
            if word in Config.LEXICON_FEAR: sad_words += 2.5
            if word in Config.LEXICON_ANGER: sad_words += 1

        percent_sad     = sad_words / len(words) * 100
        lyrical_density = len(words) / track['track']['duration_ms'] * 1000
        lyrical_valence = ((1 - (percent_sad * (1 + lyrical_density)) + 100) / 100)
        incomplete      = 'no'

    score = round((audio_valence + lyrical_valence) / 2 * 100)

    Track.insert(
        spotify_id = track['track']['id'],
        genius_id = genius_id,
        name = track['track']['name'],
        score = score,
        incomplete = incomplete
    ).execute()

    return {**track, 'lyrics': lyrical_valence, 'audio': audio_valence, 'score': score, 'incomplete': incomplete}

def get_stats(analysis):
    highest = analysis[0]
    lowest = analysis[0]

    for track in analysis:
        if track['score'] > highest['score']: highest = track
        if track['score'] < lowest['score']: lowest = track

    return {'highest': highest, 'lowest': lowest}

@app.route('/analyse', methods=['GET'])
def analyse():
    auth_header = session['auth_header']
    user        = spotify.get_users_profile(auth_header)

    if not valid_token(user):
        auth_header = spotify.authorise_client_credentials()
        user['id']  = 'me'

    playlist_id = request.args.get('playlist')
    playlist    = spotify.get_playlist(user.get('id'), playlist_id, auth_header)
    owner       = playlist['owner']['display_name'] or playlist['owner']['id']
    tracks      = spotify.get_playlist_tracks(user.get('id'), playlist_id, auth_header)

    pool     = ThreadPool(8)
    analysis = pool.map(score_track, tracks)

    playlist_valence = 0
    for track in analysis: playlist_valence += track['score']
    score = round(playlist_valence / len(analysis))

    Playlist.insert(
        playlist_id = playlist_id,
        name = playlist['name'],
        author = owner,
        date = fn.Now(),
        score = score
    ).on_conflict('replace').execute()

    return jsonify({**playlist, **get_stats(analysis), 'score': score, 'tracks': analysis})

if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)
