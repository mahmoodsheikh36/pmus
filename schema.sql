PRAGMA foreign_keys = OFF;

CREATE TABLE songs (
  name TEXT NOT NULL,
  audio_file_id INTEGER NOT NULL
  duration REAL,
  bitrate int,
  codec TEXT NOT NULL
);

CREATE TABLE song_artists (
  id INTEGER PRIMARY KEY,
  artist_id INTEGER NOT NULL,
  song_id INTEGER NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (song_id) REFERENCES songs (id)
);

CREATE TABLE album_artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id INTEGER NOT NULL,
  album_id INTEGER NOT NULL,
  time_added int,
  FOREIGN KEY (album_id) REFERENCES albums (id),
  FOREIGN KEY (artist_id) REFERENCES artists (id)
);

CREATE TABLE album_songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  song_id INTEGER NOT NULL,
  album_id INTEGER NOT NULL,
  index_in_album int,
  time_added int,
  FOREIGN KEY (album_id) REFERENCES albums (id),
  FOREIGN KEY (song_id) REFERENCES songs (id)
);

CREATE TABLE single_songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  song_id INTEGER NOT NULL,
  image_file_id INTEGER NOT NULL
  year INTEGER NOT NULL,
  time_added int,
  FOREIGN KEY (song_id) REFERENCES songs (id)
);

CREATE TABLE albums (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  year INTEGER NOT NULL,
  time_added int,
  image_file_id INTEGER NOT NULL
);

CREATE TABLE artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  time_added int
);

CREATE TABLE artist_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  image_file_id INTEGER NOT NULL,
  artist_id INTEGER NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (image_file_id) REFERENCES image_file_id (id)
);

CREATE TABLE liked_songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  song_id INTEGER NOT NULL,
  time_added int,
  FOREIGN KEY (song_id) REFERENCES songs (id)
);
