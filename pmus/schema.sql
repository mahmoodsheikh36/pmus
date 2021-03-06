PRAGMA foreign_keys = OFF;

CREATE TABLE songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  time INTEGER NOT NULL,
  audio_url TEXT NOT NULL,
  duration REAL,
  lyrics TEXT
);

CREATE TABLE song_artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id INTEGER NOT NULL,
  song_id INTEGER NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (song_id) REFERENCES songs (id)
);

CREATE TABLE album_artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id INTEGER NOT NULL,
  album_id INTEGER NOT NULL,
  FOREIGN KEY (album_id) REFERENCES albums (id),
  FOREIGN KEY (artist_id) REFERENCES artists (id)
);

CREATE TABLE album_songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  song_id INTEGER NOT NULL,
  album_id INTEGER NOT NULL,
  index_in_album INTEGER,
  FOREIGN KEY (album_id) REFERENCES albums (id),
  FOREIGN KEY (song_id) REFERENCES songs (id)
);

CREATE TABLE single_songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  song_id INTEGER NOT NULL,
  year INTEGER NOT NULL,
  time INTEGER NOT NULL,
  FOREIGN KEY (song_id) REFERENCES songs (id)
);

CREATE TABLE albums (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  year INTEGER,
  time INTEGER NOT NULL
);

CREATE TABLE artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  time INTEGER NOT NULL
);

CREATE TABLE liked_songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  song_id INTEGER NOT NULL,
  time INTEGER NOT NULL,
  FOREIGN KEY (song_id) REFERENCES songs (id)
);

CREATE TABLE playbacks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time_started INTEGER NOT NULL,
  time_ended INTEGER NOT NULL,
  song_id INTEGER NOT NULL
);

CREATE TABLE pauses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  playback_id INTEGER NOT NULL,
  FOREIGN KEY (playback_id) REFERENCES playbacks (id)
);

CREATE TABLE resumes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  playback_id INTEGER NOT NULL,
  FOREIGN KEY (playback_id) REFERENCES playbacks (id)
);

CREATE TABLE seeks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  position INTEGER NOT NULL,
  playback_id INTEGER NOT NULL,
  FOREIGN KEY (playback_id) REFERENCES playbacks (id)
);
