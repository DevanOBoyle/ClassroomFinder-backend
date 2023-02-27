/**
 * Table (and other related) definitions for the database.
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
 * All classes for a specific term.
 * Replace <term> with a valid term (like "winter2023").
 *
 * Columns:
 * - number: The class number that is unique to every class instance.
 * - code: The code associcated with a class (like "CSE115A-01").
 * - name: The shorthand name for a class (like "Intro Software Eng").
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
CREATE TABLE IF NOT EXISTS classes_<term> (
    number INTEGER,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
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
 * All instructors for classes in a specific term.
 * Replace <term> with a valid term (like "winter2023").
 *
 * Columns:
 * - class_number: The class number that is unique to every class instance.
 * - instructor: The name of an instructor teaching a class.
 *
 * Constraints:
 * - The primary key is a (class_number, instructor) pair.
 * - The class number must appear in the classes_<term> table.
 *
 * Notes:
 * - There may be multiple instructors for a specific class.
 */
CREATE TABLE IF NOT EXISTS instructors_<term> (
    class_number INTEGER,
    instructor TEXT NOT NULL,

    PRIMARY KEY (class_number, instructor),
    FOREIGN KEY (class_number) REFERENCES classes_<term>(number)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

/**
 * All meetings for classes in a specific term.
 * Replace <term> with a valid term (like "winter2023").
 *
 * Columns:
 * - class_number: The class number that is unique to every class instance.
 * - meeting_place: The location that a class meets at.
 * - meeting_time: The times that a class meets at.
 *
 * Constraints:
 * - The primary key is a (class_number, meeting_place, meeting_time) 3-tuple.
 * - The class number must appear in the classes_<term> table.
 *
 * Notes:
 * - There may be multiple meeting locations/days for a specific class.
 */
CREATE TABLE IF NOT EXISTS meetings_<term> (
    class_number INTEGER,
    meeting_place TEXT NOT NULL,
    meeting_time TEXT NOT NULL,

    PRIMARY KEY (class_number, meeting_place, meeting_time),
    FOREIGN KEY (class_number) REFERENCES classes_<term>(number)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

/**
 * All (notable) buildings on campus.
 * Building IDs are auto-generated through a sequence.
 * 
 * Columns:
 * - number: An internal number that is unique to every building.
 * - name: The full name of a building.
 * - other_names: Any other names that refer to a specific building.
 * - place_id: The Google PlaceID of the building.
 *
 * Constraints:
 * - The building number is the primary key.
 * - All building names must be unique.
 *
 * Notes:
 * - The id column is for internal use only.
 */
CREATE SEQUENCE IF NOT EXISTS building_number_seq;
CREATE TABLE IF NOT EXISTS buildings (
    number INTEGER NOT NULL DEFAULT nextval('building_number_seq'),
    name TEXT NOT NULL,
    place_id TEXT DEFAULT NULL,
    other_names TEXT[],

    PRIMARY KEY (id),
    UNIQUE (name)
);
ALTER SEQUENCE building_number_seq OWNED BY buildings.id;

/**
 * All (notable) rooms on campus.
 * 
 * Columns:
 * - building_number: An internal number that is unique to every building.
 * - name: The name of a class as it appears in the Class Search.
 * - floor: The floor the building is located on.
 * - capacity: The maximum capacity of the room.
 * - pixel_coord: Unused at this time.
 *
 * Constraints:
 * - The primary key is a (building_number, name) pair.
 * - The building number must appear in the buildings table.
 */
CREATE TABLE IF NOT EXISTS rooms (
    building_number INTEGER,
    name TEXT NOT NULL,
    number TEXT DEFAULT NULL,
    floor INTEGER DEFAULT NULL,
    capacity INTEGER DEFAULT NULL,
    pixel_coord INTEGER[],

    PRIMARY KEY (building_number, name),
    FOREIGN KEY (building_number) REFERENCES buildings(number)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- TRIGGER DEFINITIONS

/**
 * Trigger to update the last_updated row for a specific class instance
 * for a class when an UPDATE statement to a class is received.
 * Replace <term> with a valid term (like "winter2023").
 */
CREATE OR REPLACE TRIGGER update_timestamp_classes_<term>
    BEFORE UPDATE ON classes_<term>
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
