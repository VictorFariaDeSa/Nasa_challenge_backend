CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    summary TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL, 
    summary TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL, 
    summary TEXT,
    link VARCHAR(100),
    publish_date DATE
);

CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS mentions (
    topic_id SERIAL,
    mention_date DATE,
    mention_counter INT,
    PRIMARY KEY (topic_id, mention_date)
);


CREATE TABLE IF NOT EXISTS topic_category (
    topic_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (topic_id, category_id),
    FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS topic_article(
    topic_id INT NOT NULL,
    article_id INT NOT NULL,
    PRIMARY KEY (topic_id, article_id),
    FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS article_author (
    article_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (article_id, author_id),
    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE
);