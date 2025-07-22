from ytmusicapi import YTMusic
import subprocess
import os
import time
import sys
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests

# Paths
yt_dlp_path = "yt-dlp.exe"
ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
download_dir = "downloads"

def get_best_video_id(results, target_title, target_artist):
    target_title = target_title.lower()
    target_artist = target_artist.lower()

    for r in results[:5]:  # check top 5 results
        title = r.get("title", "").lower()
        artists = " ".join([a['name'] for a in r.get("artists", [])]).lower()

        if target_title in title and target_artist in artists:
            return r["videoId"]

    return None

no_match_log = open("no_good_match.txt", "a", encoding="utf-8")

# Check ffmpeg presence
if not os.path.exists(ffmpeg_path):
    print("ERROR: ffmpeg.exe not found in the script directory.")
    print("Please download it and place it next to ytdownload.py and yt-dlp.exe.")
    sys.exit(1)

# Create download folder
os.makedirs(download_dir, exist_ok=True)

# Initialize YouTube Music API
ytmusic = YTMusic()

def tag_mp3(file_path, title, artist, album, image_url=None):
            try:
                audio = EasyID3(file_path)
            except Exception:
                audio = mutagen.File(file_path, easy=True)
                audio.add_tags()

            audio["title"] = title
            audio["artist"] = artist
            audio["album"] = album
            audio.save()

            if image_url:
                try:
                    img_data = requests.get(image_url).content
                    audio = ID3(file_path)
                    audio.add(APIC(mime="image/jpeg", type=3, desc=u"Cover", data=img_data))
                    audio.save()
                except Exception as e:
                    print(f"Failed to embed album art: {e}")

# Read songs list
with open("songs.txt", "r", encoding="utf-8") as f:
    songs = []
    for line in f:
        parts = line.strip().split("|||")
        if len(parts) == 2:
            songs.append({"title": parts[0], "artist": parts[1]})


# Process each song
for song in songs:
    full_query = f"{song['title']} {song['artist']}"

    try:
        results = ytmusic.search(full_query, filter="songs")
        if not results:
            print(f"No results found for: {song}")
            continue

        title_part, artist_part = parts[0], parts[1]
        video_id = get_best_video_id(results, song['title'], song['artist'])

        if not video_id:
            msg = f"No good match for: {song['title']} by {song['artist']}"
            print(msg)
            no_match_log.write(msg + "\n")
            continue


        url = f"https://music.youtube.com/watch?v={video_id}"
        print(f"Downloading from: {url}")

        cmd = [
            yt_dlp_path,
            "-x", "--audio-format", "mp3",
            "--ffmpeg-location", os.getcwd(),
            "--output", os.path.join(download_dir, "%(title)s.%(ext)s"),
            url
        ]
        subprocess.run(cmd, check=True)

        # Infer downloaded file name
        file_name = results[0]["title"] + ".mp3"
        file_path = os.path.join(download_dir, file_name)

        # Spotify metadata enrichment (optional fallback values)
        title = results[0].get("title", song)
        artist = results[0]['artists'][0].get('name', 'Unknown')
        album = results[0].get("album", "Unknown Album")
        image_url = None

        # You could store album art from Spotify earlier if needed
        # For now, skip image_url or add if you already have it

        tag_mp3(file_path, title, artist, album, image_url)

        time.sleep(1)  # avoid getting rate-limited

    except subprocess.CalledProcessError as e:
        print(f"Download failed for {song}: {e}")
    except Exception as e:
        print(f"Error processing {song}: {e}")

    no_match_log.close()
