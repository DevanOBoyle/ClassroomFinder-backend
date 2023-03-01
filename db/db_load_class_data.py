#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loads class data into the database.
"""

import json
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


def parse_json(
        cursor,
        file: str,
        term: str,
        verbose: bool = False
        ) -> None:
    """
    Parses a JSON file and uploads its contents to the database.

    Args:
        cursor: A database cursor from a connection.
        file: The JSON file to parse.
        term: The term associated with the data.
        See "table_info.sql" for required columns.
        room: Handle room data as well.
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


def main() -> None:
    """
    Loads class data into the database.
    """
    # Program defaults.
    db_host = "cfdb.cr6zou4a0wxq.us-west-1.rds.amazonaws.com"
    db_name = "cfdb"
    db_port = "5432"

    # Parse command-line arguments.
    parser = ap.ArgumentParser(
        description="Loads JSON data into a table in the database.",
        formatter_class=ap.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "user",
        help="the user connecting to the database"
    )
    parser.add_argument(
        "pswd",
        help="the password of the user connecting to the database"
    )
    parser.add_argument(
        "file",
        help="the JSON file that will be parsed"
    )
    parser.add_argument(
        "term",
        help="the term to upload associated class data to"
    )
    parser.add_argument(
        "--db",
        default=db_name,
        help="the database to connect to"
    )
    parser.add_argument(
        "--host",
        default=db_host,
        help="the host of the database to connect to"
    )
    parser.add_argument(
        "--port",
        default=db_port,
        help="the port of the host of the database to connect to"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="verbose mode"
    )
    args = parser.parse_args()

    # Attempt to connect to the database given an account.
    try:
        conn = psycopg2.connect(
            database=args.db,
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.pswd,
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
        # Load JSON file and upload its data to the database.
        conn.autocommit = True  # Auto-commit transactions.
        if args.verbose:
            print(
                f"Account '{args.user}' connected to host '{args.host}'.\n"
                f"Loading data from '{args.file}'...\n"
            )
        with conn.cursor() as cur:
            parse_json(cur, args.file, args.term, args.verbose)
        if args.verbose:
            print(
                "\nInserted all data from JSON file.\n"
            )
        conn.close()
    return


if __name__ == "__main__":
    main()
