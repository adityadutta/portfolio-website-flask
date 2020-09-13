-- DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS project;
-- DROP TABLE IF EXISTS post;
-- DROP TABLE IF EXISTS comment;

CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE project (
  id SERIAL PRIMARY KEY,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  category TEXT,
  languages TEXT,
  link TEXT,
  date_started DATE,
  video TEXT,
  photo TEXT,
  FOREIGN KEY (author_id) REFERENCES "user" (id)
);


CREATE TABLE post (
  id SERIAL PRIMARY KEY,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  summary TEXT NOT NULL,
  category TEXT NOT NULL,
  photo TEXT,
  time_to_read INT DEFAULT 10,
  FOREIGN KEY (author_id) REFERENCES "user" (id)
);

CREATE TABLE comment (
  id SERIAL PRIMARY KEY,
  post_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  body TEXT NOT NULL,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  FOREIGN KEY (post_id) REFERENCES post (id)
);
