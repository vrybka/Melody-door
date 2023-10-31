import RPi.GPIO as GPIO
import os
import random
import time
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth


client_id = "" # REPLACE with your spotify client ID
client_secret = "" # REPLACE with your spotify client secret
device_id = '98bb0125e28656bac098d929d410c3138a4b5bcb' # REPLACE with your speaker ID, to find print(sp.devices)
redirect_uri = 'http://localhost:8080' # spotify app's redirect URI

# Reed switch connected to GPIO 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# current hour 
hour = datetime.datetime.now().hour 

# function to get song IDs from a playlist 
def get_songs_from_playlist(playlist_id):
	song_id = []
	response = sp.playlist_items(playlist_id,
								offset=0,
								fields='items.track.id',
								additional_types=['track'])
	for song in response['items']:
		song_id.append(song['track']['id'])
	return(song_id)

# infinite loop 
while True:
	# only play music between 8 a.m. and 11 p.m.
	if hour > 7 and hour < 23:

		# when door opens 
		if GPIO.input(23):

			# spotify permission scope 
			scope = "user-read-playback-state,user-modify-playback-state"
			# authenticating spotify user 
			sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,scope=scope))
			# show devices 
			# print(sp.devices()) 

			# playlist from which a song is chosen 
			playlist_id = 'spotify:playlist:3IqVc3ZggxHu9rqm1ipz8d' # REPLACE with your playlist ID

			song_ids = get_songs_from_playlist(playlist_id)
			random_song_to_play = random.choice(song_ids)

			sp.volume(0) # no music when transfering playback 
			sp.transfer_playback(device_id=device_id) # transfering playback to raspotify speaker 
			
			# playing random song from the playlist 
			sp.start_playback(uris=[f"spotify:track:{random_song_to_play}"])
			sp.volume(100)
			
			song_playing = sp.track(random_song_to_play) # saving song info 
			duration_in_sec = song_playing['duration_ms'] / 1000 # song duration in seconds 

			time.sleep(duration_in_sec) # idle for the duration of the song 
			sp.pause_playback() # pause playback after one song has played 

	time.sleep(0.1)