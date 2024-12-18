CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    surname VARCHAR(255),
    family_name VARCHAR(255)
);

CREATE TABLE t_subject (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE t_deadline (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    deadline_type VARCHAR(50),
    user_id INTEGER REFERENCES t_subject(id)
);
