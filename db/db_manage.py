#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manages various tasks related to the database.
Supports testing connectivity, adding class data for a given term,
adding building data, and adding room data.
"""
#
# IMPORTS
#


import json
import os
import sys

import argparse as ap

# Check if the psycopg2 module is installed on the system,
# as it is needed to connect to the PostgreSQL database.
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print(
        "'psycopg2' module not found. "
        "Install the 'psycopg2-binary' module through PIP.",
        file=sys.stderr
    )
    sys.exit(1)


#
# GLOBALS
#


# For type hinting.
FilePath = str | bytes | os.PathLike


#
# CLASSES AND FUNCTIONS
#


def read_env(file: FilePath = ".env") -> dict | None:
    """
    Reads in environment variables for the script from a file.
    Stores variables in a dictionary.

    Args:
        file: The file to read variables from. Defaults to ".env".

    Return:
        Returns a dictionary with all parsed environment variables,
        or None if an error occurs (file not found, permissions, etc.).
    """
    # Open the file.
    # If the file fails to open, return None.
    env = None
    try:
        with open(file, 'r') as f:
            lines = [line.strip().split('=') for line in f.readlines()]
            env = {key: val for key, val in lines}
    except (FileNotFoundError, PermissionError):
        return None
    return env


def load_building_data(
    cursor,
    file: FilePath,
    verbose: bool = False
) -> None:
    """
    Parses a JSON file containing building data and uploads its contents to
    the database.

    Args:
        cursor: A database cursor from a connection.
        file: The JSON file to parse.
        verbose: Verbose mode; prints what is happening to ``stdout``.
    """
    # Open the JSON file as a dictionary.
    # The buildings dictionary contains a list of individual buildings
    # with the respective information for each building.
    with open(file, 'r', newline='') as json_file:
        building_data = json.load(json_file)
        for building_info in building_data['buildings']:
            # Insert into the table.
            # This method prevents SQL-injection.
            # https://www.psycopg.org/docs/sql.html#module-usage
            if verbose:
                print(
                    f"Inserting building:\n"
                    f"- Name: {building_info['name']}\n"
                    f"- PlaceID: {building_info['place_id']}"
                )
            cursor.execute(
                sql.SQL(
                    '''
                    INSERT INTO buildings(name, place_id, other_names)
                        VALUES (%s, %s, %s)
                    '''
                ),
                (
                    building_info['name'],
                    building_info['place_id'],
                    building_info['other_names']
                )
            )
            if verbose:
                print(
                    f"Successfully added {building_info['name']}."
                )
    return


def load_class_data(
    cursor,
    file: FilePath,
    term: str,
    verbose: bool = False
) -> None:
    """
    Parses a JSON file containing class data for a specific term
    and uploads its contents to the database.

    Args:
        cursor: A database cursor from a connection.
        file: The JSON file to parse.
        term: The term associated with the data.
        verbose: Verbose mode; prints what is happening to ``stdout``.
    """
    # Open the JSON file as a large dictionary.
    # The classes dictionary contains a list of individual classes
    # with the respective information for each class.
    with open(file, 'r', newline='') as json_file:
        class_data = json.load(json_file)
        for class_info in class_data['classes']:
            # Insert into the table.
            # This method prevents SQL-injection.
            # https://www.psycopg.org/docs/sql.html#module-usage
            if verbose:
                print(
                    f"Inserting class:\n"
                    f"- Number: {class_info['number']}\n"
                    f"- Code: {class_info['code']}\n"
                    f"- Name: {class_info['name']}\n"
                    f"- Instructor(s): {class_info['instructors']}\n"
                    f"- Meeting(s): {class_info['meetings']}\n"
                    f"- Mode: {class_info['mode']}\n"
                    f"- Last Updated: {class_info['last_updated']}"
                )

            # First insert class information.
            cursor.execute(
                sql.SQL(
                    '''
                    INSERT INTO {}(
                        number,
                        code,
                        name,
                        mode,
                        last_updated
                    )
                        VALUES (%s, %s, %s, %s, %s)
                    '''
                ).format(sql.Identifier(f'classes_{term.lower()}')),
                (
                    class_info['number'],
                    class_info['code'],
                    class_info['name'],
                    class_info['mode'],
                    class_info['last_updated']
                )
            )

            # Then add all instructor information.
            for instructor in class_info['instructors']:
                cursor.execute(
                    sql.SQL(
                        '''
                        INSERT INTO {}(
                            class_number,
                            instructor
                        )
                            VALUES (%s, %s)
                        '''
                    ).format(sql.Identifier(f'instructors_{term.lower()}')),
                    (
                        class_info['number'],
                        instructor
                    )
                )

            # Finally, add all meeting information.
            for meeting in class_info['meetings']:
                if len(meeting) == 3:  # Multiple times in one place.
                    cursor.execute(
                        sql.SQL(
                            '''
                            INSERT INTO {}(
                                class_number,
                                meeting_place,
                                meeting_time
                            )
                                VALUES (%s, %s, %s)
                            '''
                        ).format(sql.Identifier(f'meetings_{term.lower()}')),
                        (
                            class_info['number'],
                            meeting[0],
                            meeting[1]
                        )
                    )
                    cursor.execute(
                        sql.SQL(
                            '''
                            INSERT INTO {}(
                                class_number,
                                meeting_place,
                                meeting_time
                            )
                                VALUES (%s, %s, %s)
                            '''
                        ).format(sql.Identifier(f'meetings_{term.lower()}')),
                        (
                            class_info['number'],
                            meeting[0],
                            meeting[2]
                        )
                    )
                else:
                    cursor.execute(
                        sql.SQL(
                            '''
                            INSERT INTO {}(
                                class_number,
                                meeting_place,
                                meeting_time
                            )
                                VALUES (%s, %s, %s)
                            '''
                        ).format(sql.Identifier(f'meetings_{term.lower()}')),
                        (
                            class_info['number'],
                            meeting[0],
                            meeting[1]
                        )
                    )

            if verbose:
                print(
                    f"Successfully added {class_info['code']}: "
                    f"{class_info['name']}."
                )
    return


def load_room_data(
    cursor,
    term: str,
    verbose: bool = False
) -> None:
    """
    Parses meetings for a specific term to find any undefined rooms.
    Given the non-uniform nature of the data, requires user input.

    Args:
        cursor: A database cursor from a connection.
        term: The term associated with the data.
        verbose: Verbose mode; prints what is happening to ``stdout``.
    """
    # Fetch all meeting places from the specified term.
    # Only get meeting places that are physical locations.
    cursor.execute(
        sql.SQL(
            '''
            SELECT meeting_place FROM {}
            WHERE meeting_place != ''
                OR meeting_place LIKE 'Remote %'
                OR meeting_place != 'Online'
                OR meeting_place != 'TBD In Person'
            '''
        ).format(sql.Identifier(f'meetings_{term.lower()}'))
    )
    places = cursor.fetchall()

    # Parse through all found meeting places.
    # For each place, the user must input what is asked.
    for place in places:
        # Existence check; see if the place already exists as a room.
        # If so, skip to the next place.
        location = place[0]  # The place is a 1-tuple.
        cursor.execute(
            '''
            SELECT 1 FROM rooms WHERE name = %s
            ''',
            (location, )
        )
        res = cursor.fetchone()
        if res:
            if verbose:
                print(f"{location} already exists; skipping.")
            continue

        # If room does not exist, attempt to add it.
        # The user will be asked a number of questions that will be added
        # to the database.
        # First, ask the building number associated with the room.
        building_num = input(
            f"Enter building number for {location} (leave blank to skip): "
        )
        if not len(building_num):
            print(f"- Skipping {location}.")
            continue

        # Next, ask the room number associated with the room.
        room_num = input(
            f"Enter room number for {location} (leave blank for NULL): "
        )
        if len(room_num) == 0:
            room_num = None

        # Next, ask the floor that the room is on.
        floor = input("Enter floor (leave blank for NULL): ")
        if len(floor) == 0:
            floor = None
        else:
            floor = int(floor)

        # Finally, ask the capacity of the room.
        capacity = input("Enter capacity (leave blank for NULL): ")
        if len(capacity) == 0:
            capacity = None
        else:
            capacity = int(capacity)

        # All information has been collected.
        # Add the room to the database.
        if verbose:
            print(f"Adding {location}...")
        cursor.execute(
            '''
            INSERT INTO rooms(building_number, name, number, floor, capacity)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (
                building_num,
                location,
                room_num,
                floor,
                capacity
            )
        )
        print(f"Added {location}.")
    return


def main() -> None:
    """
    Perform some management tasks on the database.
    """
    # Program defaults.
    db_host = "cfdb.cr6zou4a0wxq.us-west-1.rds.amazonaws.com"
    db_name = "cfdb"
    db_port = "5432"
    db_user = None
    db_pswd = None

    # Parse command-line arguments.
    parser = ap.ArgumentParser(
        description="Perform database tasks.",
        epilog="Only one task can be performed at a time."
    )
    parser.add_argument(
        "-u",
        "--user",
        help="the user connecting to the database"
    )
    parser.add_argument(
        "-p",
        "--pswd",
        help="the password of the user connecting to the database"
    )
    parser.add_argument(
        "-f",
        "--file",
        help="the JSON file requested by some tasks"
    )
    parser.add_argument(
        "-t",
        "--term",
        help="the term requested by some tasks"
    )
    parser.add_argument(
        "--load_class_data",
        action="store_true",
        help="loads class data into the database (requires '-f/--file' and '-t/--term' args)"
    )
    parser.add_argument(
        "--load_building_data",
        action="store_true",
        help="loads building data into the database (requires '-f/--file' arg)"
    )
    parser.add_argument(
        "--load_room_data",
        action="store_true",
        help="loads room data into the database (requires '-t/--term' arg)"
    )
    parser.add_argument(
        "-e",
        "--env",
        action="store_true",
        help="read environment variables from .env file"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose mode"
    )
    args = parser.parse_args()

    # Set program variables.
    # Read from environment variables file if specified.
    if args.env:
        if args.verbose:
            print(
                "Reading environment variables 'DB_USER' and 'DB_PSWD'..."
            )
        env_vars = read_env()
        try:
            db_user = env_vars['DB_USER']
            db_pswd = env_vars['DB_PSWD']
        except KeyError:
            print(
                "'.env' file does not contain required variables.",
                file=sys.stderr
            )
            sys.exit(1)

    # Check if username and password are still None.
    if not db_user or not db_pswd:
        print(
            "No username and/or password provided.\n"
            "Use '-e/--env' to read from .env file, "
            "or provide username and password with "
            "'-u/--user' and '-p/--pswd'.",
            file=sys.stderr
        )
        sys.exit(1)

    # Attempt to connect to the database given an account.
    try:
        conn = psycopg2.connect(
            database=db_name,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pswd,
        )
    except psycopg2.OperationalError as e:
        # Attempt failed.
        print(
            f"{str(e)}",
            file=sys.stderr
        )
        sys.exit(1)
    else:
        # Attempt successful.
        # If a task is specified, start doing it.
        if args.verbose:
            print(
                f"Account '{db_user}' connected to host '{db_host}'."
            )
        if args.load_class_data:
            with conn.cursor() as cur:
                if not args.file or not args.term:
                    print(
                        "'--load_class_data' requires "
                        "'-f/--file' and -t/--term' to be set.",
                        file=sys.stderr
                    )
                    sys.exit(1)
                load_class_data(cur, args.file, args.term, args.verbose)
                conn.commit()
        elif args.load_building_data:
            with conn.cursor() as cur:
                if not args.file:
                    print(
                        "'--load_building_data' requires "
                        "'-f/--file' to be set.",
                        file=sys.stderr
                    )
                    sys.exit(1)
                load_building_data(cur, args.file, args.verbose)
                conn.commit()
        elif args.load_room_data:
            with conn.cursor() as cur:
                if not args.term:
                    print(
                        "'--load_room_data' requires "
                        "'-t/--term' to be set.",
                        file=sys.stderr
                    )
                    sys.exit(1)
                load_room_data(cur, args.term, args.verbose)
                conn.commit()

        # Once the task is finished, close.
        if args.verbose:
            print(
                "Closing management script."
            )
        conn.close()
    return


if __name__ == "__main__":
    main()
