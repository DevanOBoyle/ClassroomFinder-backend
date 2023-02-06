/**
 * Table definitions for the database.
 * These are valid SQL.
 */

/**
 * All classes for the quarter of Winter 2023.
 */
CREATE TABLE IF NOT EXISTS classes_winter2023 (
    number INTEGER,
    code VARCHAR(20),
    name VARCHAR(100),
    instructor VARCHAR(50),
    room VARCHAR(50) DEFAULT NULL,
    days VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (number)
);

/**
 * All buildings.
 * 
 * Notes:
 * - The 'id' column is for internal use only; don't insert to it.
 */
CREATE SEQUENCE buildings_id_seq;
CREATE TABLE IF NOT EXISTS buildings (
    id INTEGER NOT NULL DEFAULT nextval('buildings_id_seq'),
    name VARCHAR(100) NOT NULL,
    placeid VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE (name)
);
ALTER SEQUENCE buildings_id_seq OWNED BY buildings.id;
