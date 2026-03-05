# Spotify Wikipedia Playlist Generator

This script scrapes a category page of musical groups from Wikipedia and automatically creates a Spotify playlist containing the top tracks of those artists.

## Prerequisites

You need to create a Spotify Developer Application to get credentials to interact with the Spotify API.

### 1. Create a Spotify App
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log in with your Spotify account.
3. Click on **Create app**.
4. Give it an App Name and App Description (e.g., "Wiki Playlist Generator").
5. In the **Redirect URIs** field, enter: `http://localhost:8888/callback`
6. Click **Save**.

### 2. Get Credentials
Once your app is created, go to the **Settings** of the app.
1. Copy the **Client ID**.
2. Click "View client secret" and copy the **Client Secret**.

## Setup Instructions

1. **Install Python details**:
   Open a terminal and navigate to this folder, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set passing variables in your terminal**:
   (Replace `your_client_id` and `your_client_secret` with the ones from your Spotify dashboard).
   ```bash
   export SPOTIPY_CLIENT_ID='your_client_id'
   export SPOTIPY_CLIENT_SECRET='your_client_secret'
   export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
   ```

## Usage

Simply run the script. It uses an example Finnish Melodic Death Metal Wikipedia url by default:

```bash
python main.py
```

*Note: The first time you run this, it will open your web browser asking you to authorize the app with your Spotify account. After you log in and agree, you'll be redirected to a localhost URL. Copy the full URL from your browser's address bar and paste it back into the terminal.*

**Using a custom URL**:
You can pass any Wikipedia Category URL as an argument, and the script will automatically parse the URL to create a descriptive, **private** playlist for you (e.g., "Spotipy swedish synth-pop groups bands"):
```bash
python main.py "https://en.wikipedia.org/wiki/Category:Swedish_synth-pop_groups"
```

**Override Playlist Name:**
You can also pass a second argument to manually name the playlist:
```bash
python main.py "https://en.wikipedia.org/wiki/Category:Swedish_synth-pop_groups" "My Custom Name"
```
