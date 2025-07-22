import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="cd88df78cc2142ddbbf32896b756ac98",
    client_secret="faae6d3817db459e91cd922eebed2175"
))

playlist_id = "0AmZtyirrpOATm69XpAlw0"
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


