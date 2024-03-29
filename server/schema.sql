DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS auth;
DROP TABLE IF EXISTS client_secret;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  strava_data BOOLEAN DEFAULT 0 
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE auth (
  id INTEGER PRIMARY KEY,
  expires_at INTEGER NOT NULL,
  refresh_token TEXT NOT NULL,
  access_token TEXT NOT NULL
);

CREATE TABLE client_secret (
  secret_name TEXT PRIMARY KEY,
  secret_value TEXT NOT NULL
);