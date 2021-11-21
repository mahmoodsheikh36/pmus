PRAGMA foreign_keys = OFF;

CREATE TABLE tracks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  audio_file_path TEXT NOT NULL,
  duration REAL NOT NULL,
  album_id INTEGER NOT NULL,
  index_in_album INTEGER NOT NULL,
  lyrics TEXT
);

CREATE TABLE track_artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id INTEGER NOT NULL,
  track_id INTEGER NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (track_id) REFERENCES tracks (id)
);

CREATE TABLE album_artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id INTEGER NOT NULL,
  album_id INTEGER NOT NULL,
  FOREIGN KEY (album_id) REFERENCES albums (id),
  FOREIGN KEY (artist_id) REFERENCES artists (id)
);

CREATE TABLE albums (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  year INTEGER
);

CREATE TABLE artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
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
