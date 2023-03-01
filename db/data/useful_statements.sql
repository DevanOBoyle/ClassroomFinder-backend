/**
 * Potentially useful statements for querying the database.
 * These are valid SQL.
 */

/**
 * General tips:
 * - If you want to associate class data with building data,
 *   you will need to do the following in order:
 *   1. Join the 'classes_<term>' table with its associated 'meetings_<term>' table.
 *      Join the two on 'number' for 'classes_<term>' and 'class_number' for 'meetings_<term>'.
 *   2. Join the 'rooms' table with the 'meetings_<term>' table.
 *      Join the two on 'name' for 'rooms' and 'meeting_place' for 'meetings_<term>'.
 *   3. Join the 'buildings' table with the 'rooms' table.
 *      Join the two on 'number' for 'buildings' and 'building_number' for 'rooms'.
 */

/**
 * Queries everything: class number, class code, class name, class instructors,
 * class meeting locations and times, full building names, and building PlaceIDs.
 * Replace <term> with desired term.
 */
SELECT (c.number, 
        c.code, 
        c.name, 
        i.instructor, 
        m.meeting_time, 
        m.meeting_place, 
        b.name AS building_name, 
        b.place_id)
FROM classes_<term> AS c
JOIN instructors_<term> AS i ON i.class_number = c.number
JOIN meetings_<term> AS m ON m.class_number = c.number
JOIN rooms AS r ON r.name = m.meeting_place
JOIN buildings AS b ON b.number = r.building_number;

/**
 * Queries class number, class code, class name, class meeting times,
 * full building names, and building PlaceIDs given a room name.
 * Replace <term> with desired term, and <room name> with desired room name.
 */
SELECT (c.number,
        c.code,
        c.name,
        m.meeting_time,
        b.name AS building_name,
        b.place_id)
FROM classes_<term> AS c
JOIN meetings_<term> AS m on m.class_number = c.number
JOIN rooms as r on r.name = m.meeting_place
JOIN buildings as b on b.number = r.building_number
WHERE m.meeting_place = '<room name>';


