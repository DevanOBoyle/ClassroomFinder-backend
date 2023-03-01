#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loads building data into the database.
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


def parse_json(cursor, file: str, verbose: bool = False) -> None:
    """
    Parses a JSON file and uploads its contents to the database.

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


def main() -> None:
    """
    Loads building data into the database.
    """
    # Program defaults.
    db_host = "cfdb.cr6zou4a0wxq.us-west-1.rds.amazonaws.com"
    db_name = "cfdb"
    db_port = "5432"

    # Parse command-line arguments.
    parser = ap.ArgumentParser(
        description="Loads data from a JSON file into a table in the database.",
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
                f"Loading data from '{args.file}' into table 'buildings'...\n"
            )
        with conn.cursor() as cur:
            parse_json(cur, args.file, args.verbose)
        if args.verbose:
            print(
                "\nInserted all data from JSON file.\n"
            )
        conn.close()
    return


if __name__ == "__main__":
    main()
