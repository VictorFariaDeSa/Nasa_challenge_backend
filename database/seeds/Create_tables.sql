CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    summary TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50), 
    summary TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50), 
    summary TEXT,
    link VARCHAR(100),
    publish_date DATE
);