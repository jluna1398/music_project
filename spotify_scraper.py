import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from firebase_admin import firestore
from firebase_admin import credentials, initialize_app
from dotenv import load_dotenv, dotenv_values
import os



spotify_client_id = os.getenv("SPOTIPY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(spotify_client_id, spotify_client_secret))
config = dotenv_values(".env")
cred = credentials.Certificate(config)
initialize_app(cred)
db = firestore.client()

def get_track_stats(track_id: str):
    audio_return = spotify.audio_features(track_id)[0]
    exclude_keys = ['id', 'uri', 'duration_ms', 'track_href', 'type']
    filtered_data = {key: value for key, value in audio_return.items() if key not in exclude_keys}
    return filtered_data


def get_all_genres(artist_ids):
    all_genres = []  # List to store all genres

    for artist_id in artist_ids:
        try:
            artist = spotify.artist(artist_id)
            genres = artist['genres']

            if genres:
                all_genres.extend(genres)
            else:
                print(f"No genres found for artist with ID {artist_id}")
        except Exception as e:
            print(f"Error fetching artist genres for ID {artist_id}: {e}")

    return all_genres


def get_track_album(album: str):
    res = spotify.playlist_tracks(playlist_id=album)["items"]

    for i in res:
        result_dict = {}
        data = i["track"]
        result_dict["album_name"] = data.get("album", {}).get("name")
        result_dict["album_id"] = data.get("album", {}).get("id")
        artists = data.get("album", {}).get("artists", [])
        result_dict["artist_names"] = [artist.get("name") for artist in artists]
        result_dict["artist_uri"] = [artist.get("uri") for artist in artists]
        artist_id = [artist.get("id") for artist in artists]
        result_dict["artist_id"] = artist_id
        result_dict["track_name"] = data.get("name")
        result_dict["track_uri"] = data.get("uri")
        track_id = data.get("id")
        result_dict["track_id"] = track_id
        result_dict["track_image"] = data.get("album", {}).get("images", [])[1].get("url")
        genres = get_all_genres(artist_id)
        result_dict["genres"] = genres
        track_features = get_track_stats(track_id)
        result_dict.update(track_features)

        doc_ref = db.collection(u'track').document(track_id)
        doc_ref.set(result_dict)


get_track_album("open.spotify.com/playlist/37i9dQZF1DWX5ZOsG2Ogi1")








# def serch_track(id: str):
#     search_track_res = spotify.track(id)
#     return search_track_res
#
# serch_track("")
