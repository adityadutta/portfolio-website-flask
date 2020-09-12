-- DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS post;

-- CREATE TABLE user (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   username TEXT UNIQUE NOT NULL,
--   password TEXT NOT NULL
-- );

-- CREATE TABLE project (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   title TEXT NOT NULL,
--   summary TEXT NOT NULL,
--   category TEXT,
--   languages TEXT,
--   link TEXT,
--   date_started DATE,
--   video TEXT,
--   photo TEXT,
--   FOREIGN KEY (author_id) REFERENCES user (id)
-- );


CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  summary TEXT NOT NULL,
  category TEXT NOT NULL,
  photo TEXT,
  time_to_read INT DEFAULT 10,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
