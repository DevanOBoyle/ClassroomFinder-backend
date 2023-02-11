/**
 * Table (and other related) definitions for the database.
 * These are valid SQL.
 */

-- FUNCTION DEFINITIONS

/**
 * Function to update the last_updated column with the current UTC time.
 */
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = DATE_TRUNC('second', (NOW() at time zone 'utc'));
    return NEW;
END;
$$ LANGUAGE plpgsql;


-- TABLE DEFINITIONS

/**
 * All classes for the quarter of Winter 2023.
 *
 * Columns:
 * - number: The class number that is unique to every class instance.
 * - code: The code associcated with a class (like "CSE115A-01").
 * - name: The shorthand name for a class (like "Intro Software Eng").
 * - instructors: An array of instructors teaching a class.
 * - meetings: A two-dimensional array of {location, days and times} pairs.
 * - mode: How the class is being taught.
 * - last_updated: When a specific class entry was last updated.
 *
 * Constraints:
 * - The class number is the primary key.
 * - All class codes must be unique.
 * - The class mode must be a supported mode.
 *
 * Notes:
 * - The last_updated timestamp should be in UTC.
 */
CREATE TABLE IF NOT EXISTS classes_winter2023 (
    number INTEGER,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    instructors TEXT[],
    meetings TEXT[][],
    mode TEXT NOT NULL,
    last_updated TIMESTAMP WITHOUT TIME ZONE 
        DEFAULT DATE_TRUNC('second', (NOW() at time zone 'utc')),

    PRIMARY KEY (number),
    UNIQUE (code),

    CONSTRAINT valid_mode
        CHECK (mode IN (
            'In Person',
            'Hybrid',
            'Asynchronous Online',
            'Synchronous Online'
            )
        ) 
);

/**
 * All (notable) buildings on campus.
 * Building IDs are auto-generated through a sequence.
 * 
 * Columns:
 * - id: An internal number that is unique to every building instance.
 * - name: The full name of a building.
 * - other_names: Any other names that refer to a specific building.
 * - place_id: The Google PlaceID of the building.
 *
 * Constraints:
 * - The building ID is the primary key.
 * - All building names must be unique.
 *
 * Notes:
 * - The id column is for internal use only.
 */
CREATE SEQUENCE IF NOT EXISTS buildings_id_seq;
CREATE TABLE IF NOT EXISTS buildings (
    id INTEGER NOT NULL DEFAULT nextval('buildings_id_seq'),
    name TEXT NOT NULL,
    other_names TEXT[],
    place_id TEXT DEFAULT NULL,

    PRIMARY KEY (id),
    UNIQUE (name)
);
ALTER SEQUENCE buildings_id_seq OWNED BY buildings.id;


-- TRIGGER DEFINITIONS

/**
 * Trigger to update the last_updated row for a specific class instance
 * for a Winter 2023 class when an UPDATE statement to a class is received.
 */
CREATE OR REPLACE TRIGGER update_timestamp_classes_winter2023
    BEFORE UPDATE ON classes_winter2023
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
