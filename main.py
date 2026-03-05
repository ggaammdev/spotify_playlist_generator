import os
import sys
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_bands_from_wiki(url):
    """
    Scrape a Wikipedia category page for band names.
    This targets the 'mw-pages' div which typically contains the alphabetical list of pages in the category.
    """
    print(f"Fetching Wikipedia page: {url}")
    headers = {
        'User-Agent': 'SpotifyPlaylistGenerator/1.0 (Contact: user@example.com)'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    bands = []
    category_div = soup.find('div', id='mw-pages')
    if not category_div:
        print("Could not find 'mw-pages' div on the Wikipedia page. The structure might be different.")
        return bands
        
    # The bands are usually inside list items within this div
    for li in category_div.find_all('li'):
        a_tag = li.find('a')
        if a_tag:
            # We take the text of the link which is the page/band name
            # Sometime Wikipedia adds (band) or (musician), we can clean that if needed
            band_name = a_tag.text
            # Remove basic parentheticals like "(band)" to improve Spotify search accuracy
            if "(band)" in band_name:
                band_name = band_name.replace("(band)", "").strip()
            bands.append(band_name)
            
    return bands

def create_spotify_playlist(bands, playlist_name="Wiki Generated Playlist"):
    """
    Search for bands on Spotify, get their top tracks, and add to a new playlist.
    """
    print("\nAuthenticating with Spotify...")
    # This will trigger a browser window to open for you to log in to Spotify 
    # and authorize the app. It relies on environment variables:
    # SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI
    scope = "playlist-modify-public playlist-modify-private user-read-private user-read-email"
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        user_id = sp.current_user()['id']
    except Exception as e:
        print("\n[!] Failed to authenticate with Spotify.")
        print("Please ensure you have set the following environment variables:")
        print(" - SPOTIPY_CLIENT_ID")
        print(" - SPOTIPY_CLIENT_SECRET")
        print(" - SPOTIPY_REDIRECT_URI")
        print(f"Error details: {e}")
        return

    print(f"Authenticated as user: {user_id}")
    print(f"DEBUG - Full User Object: {sp.current_user()}")
    print(f"Creating private playlist: '{playlist_name}'...")
    try:
        # Get the underlying access token from spotipy
        token = sp.auth_manager.get_access_token(as_dict=False)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test creating playlist via direct request. Feb 2026 API uses /me/playlists
        create_url = "https://api.spotify.com/v1/me/playlists"
        data = {
            "name": playlist_name,
            "public": False,
            "description": "Auto-generated playlist"
        }
        
        print(f"DEBUG - Making direct POST to {create_url}")
        res = requests.post(create_url, headers=headers, json=data)
        
        if res.status_code not in (200, 201):
            print(f"\n[!] Direct API Error {res.status_code}: {res.text}")
            return
            
        playlist = res.json()
        playlist_id = playlist['id']
        
    except Exception as e:
        print(f"\n[!] Direct Request Failed: {e}")
        return
    
    track_uris = []
    print("\nSearching for bands and gathering top tracks...")
    for band in bands:
        # Search directly for tracks by the artist (bypasses removed 'top-tracks' endpoint)
        result = sp.search(q=f"artist:{band}", type='track', limit=2)
        tracks = result.get('tracks', {}).get('items', [])
        
        if not tracks:
            print(f"  [-] No tracks found for: {band}")
            continue
            
        # Optional: Print the artist name from the first track found
        actual_artist_name = tracks[0]['artists'][0]['name']
        print(f"  [+] Found tracks for: {actual_artist_name}")
        
        for track in tracks:
            track_uris.append(track['uri'])
                
    if track_uris:
        print(f"\nAdding {len(track_uris)} tracks to the playlist...")
        # Spotify allows adding a maximum of 100 tracks per request
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i+100]
            add_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
            res = requests.post(add_url, headers=headers, json={"uris": batch})
            if res.status_code not in (200, 201):
                print(f"  [!] Failed to add batch {i}: {res.status_code} {res.text}")
        
        print("\nSuccess! Playlist created.")
        print(f"Check your Spotify account for: '{playlist_name}'")
        print(f"Playlist Link: {playlist['external_urls']['spotify']}")
    else:
        print("\nNo tracks were found to add to the playlist.")

if __name__ == "__main__":
    import urllib.parse
    
    # You can pass a Wikipedia URL as an argument, otherwise it defaults to the Finnish death metal example
    default_url = "https://en.wikipedia.org/wiki/Category:Finnish_melodic_death_metal_musical_groups"
    
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    # Optional: Customize the playlist name from args or default
    if len(sys.argv) > 2:
        playlist_name = sys.argv[2]
    elif url == default_url:
        playlist_name = "Finnish Melodic Death Metal Favorites"
    else:
        # Parse a nice name from URL like: Category:Swedish_death_metal_musical_groups
        try:
            raw_name = urllib.parse.unquote(url.split(':')[-1])
            clean_name = raw_name.replace('_musical_groups', '').replace('_bands', '').replace('_', ' ')
            playlist_name = f"Spotipy {clean_name.lower()} bands"
        except Exception:
            playlist_name = "Wikipedia Selected Bands"
    
    bands = get_bands_from_wiki(url)
    print(f"\nExtracted {len(bands)} bands from Wikipedia.")
    
    if bands:
        create_spotify_playlist(bands, playlist_name=playlist_name)
