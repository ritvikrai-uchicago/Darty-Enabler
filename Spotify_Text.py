import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id= NULL,
    client_secret= NULL
))

playlist_id = NULL
results = sp.playlist_tracks(playlist_id)


# Function to fetch all songs using pagination
def get_all_tracks(sp, playlist_id):
    songs = []
    offset = 0
    limit = 100

    while True:
        response = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        items = response['items']
        if not items:
            break

        for item in items:
            track = item['track']
            if track:
                name = track.get('name')
                artist = track['artists'][0].get('name') if track['artists'] else "Unknown"
                songs.append({"title": name, "artist": artist})

        offset += limit

    return songs

# Run and save
songs = get_all_tracks(sp, playlist_id)

with open("songs.txt", "w", encoding="utf-8") as f:
    for song in songs:
        f.write(f"{song['title']}|||{song['artist']}\n")


