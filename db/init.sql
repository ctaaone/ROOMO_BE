-- init.sql

-- CREATE DATABASE main_db;

-- Connect to main_db
\c main_db  

CREATE EXTENSION postgis;

CREATE TABLE space_types (
    id SERIAL PRIMARY KEY,
    type_name TEXT NOT NULL
);

CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE spaces (
    id SERIAL PRIMARY KEY,
    provider_id SERIAL REFERENCES providers(id) ON DELETE CASCADE, 
    name TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    address TEXT,
    abstract TEXT,
    desc_summary TEXT,
    review_summary TEXT,
    description TEXT,
    agent_rule TEXT,
    space_type TEXT,
    price TEXT,
    capacity TEXT
);

CREATE TABLE inquiries (
    id SERIAL PRIMARY KEY,
    space_id SERIAL REFERENCES spaces(id) ON DELETE CASCADE,
    content TEXT
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id SERIAL REFERENCES users(id) ON DELETE CASCADE,
    space_id SERIAL REFERENCES spaces(id) ON DELETE CASCADE,
    content TEXT
);

CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    user_id SERIAL REFERENCES users(id) ON DELETE CASCADE,
    space_id SERIAL REFERENCES spaces(id) ON DELETE CASCADE,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);
