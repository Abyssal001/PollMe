DROP TABLE IF EXISTS polls;
CREATE TABLE polls (
  id integer PRIMARY KEY AUTOINCREMENT,
  question text NOT NULL,
  is_multi boolean DEFAULT TRUE,
  create_at integer
);

DROP TABLE IF EXISTS options;
CREATE TABLE options (
  id integer PRIMARY KEY AUTOINCREMENT,
  poll_id integer NOT NULL,
  option integer NOT NULL,
  content text NOT NULL,
  voters integer DEFAULT 0
);

DROP TABLE IF EXISTS votes;
CREATE TABLE votes (
  id integer PRIMARY KEY AUTOINCREMENT,
  poll_id integer NOT NULL,
  option_id integer NOT NULL,
  ip text NOT NULL
);