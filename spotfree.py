import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'CLIENT ID'  # Replace With Your Own Spotify Dev Client ID
SPOTIPY_CLIENT_SECRET = 'CLIENT KEY' # Replace With Your Own Spotify Dev Client KEY

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                           client_secret=SPOTIPY_CLIENT_SECRET))

def fetch_spotify_playlist(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    songs = []
    for item in tracks:
        track = item['track']
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        songs.append(f"{song_name} by {artist_name}")
    
    return songs

def download_song_from_youtube(song_name, progress_callback=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{song_name}.%(ext)s',
        'noplaylist': True,
        'progress_hooks': [progress_callback] if progress_callback else [],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch1:{song_name}"])

class SpotifyDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Playlist Downloader")
        self.root.geometry("600x400")
        
        # Main Frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Playlist ID Entry
        self.playlist_id_label = ttk.Label(self.main_frame, text="Spotify Playlist ID:")
        self.playlist_id_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.playlist_id_entry = ttk.Entry(self.main_frame, width=50)
        self.playlist_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Buttons
        self.fetch_button = ttk.Button(self.main_frame, text="Fetch Playlist", command=self.fetch_playlist)
        self.fetch_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.clear_button = ttk.Button(self.main_frame, text="Clear", command=self.clear_playlist)
        self.clear_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Song Listbox
        self.song_listbox = tk.Listbox(self.main_frame, selectmode=tk.MULTIPLE, width=70, height=15)
        self.song_listbox.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.song_listbox.yview)
        self.song_listbox.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=4, sticky="ns")
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        
        # Download Button
        self.download_button = ttk.Button(self.main_frame, text="Download Selected Songs", command=self.download_selected_songs)
        self.download_button.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
    
    def fetch_playlist(self):
        playlist_id = self.playlist_id_entry.get()
        if not playlist_id:
            messagebox.showerror("Error", "Please enter a Spotify Playlist ID")
            return
        
        self.status_var.set("Fetching playlist...")
        self.root.update_idletasks()
        
        try:
            songs = fetch_spotify_playlist(playlist_id)
            self.song_listbox.delete(0, tk.END)
            for song in songs:
                self.song_listbox.insert(tk.END, song)
            self.status_var.set(f"Fetched {len(songs)} songs. Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch playlist: {e}")
            self.status_var.set("Ready")
    
    def clear_playlist(self):
        self.song_listbox.delete(0, tk.END)
        self.status_var.set("Playlist cleared. Ready")
    
    def download_selected_songs(self):
        selected_songs = self.song_listbox.curselection()
        if not selected_songs:
            messagebox.showerror("Error", "Please select at least one song to download")
            return
        
        self.progress_bar["maximum"] = len(selected_songs)
        self.progress_bar["value"] = 0
        self.status_var.set("Starting download...")
        self.root.update_idletasks()
        
        for i, index in enumerate(selected_songs):
            song_name = self.song_listbox.get(index)
            self.status_var.set(f"Downloading: {song_name}")
            self.root.update_idletasks()
            
            try:
                download_song_from_youtube(song_name, self.update_progress)
                self.progress_bar["value"] = i + 1
                self.root.update_idletasks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download {song_name}: {e}")
        
        self.status_var.set("Download complete. Ready")
        messagebox.showinfo("Success", "All selected songs have been downloaded.")

    def update_progress(self, d):
        if d['status'] == 'downloading':
            self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpotifyDownloaderApp(root)
    root.mainloop()
