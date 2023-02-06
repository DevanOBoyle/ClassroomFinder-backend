#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loads class data into the database.
"""

import csv
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


def parse_csv(cursor, file: str, table: str, verbose: bool = False) -> None:
    """
    Parses a csv file and uploads its contents to the database.

    Args:
        cursor: A database cursor from a connection.
        file: The csv file to parse.
        table: The table in the database to store the csv file data.
        Must have columns 'code', 'name', 'number', 'instructor', 'room',
        and 'days'.
        verbose: Verbose mode; prints what is happening to ``stdout``.
    """
    # Open the csv file and parse its contents.
    # Each row is a 6-length list in the following order:
    # - class code
    # - class name
    # - class number
    # - instructor name
    # - building and room
    # - days and time
    with open(file, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            # Split the row into its columns.
            # Before inserting, fix any errors.
            code, name, number, instructor, room, days = row

            # If the room is an empty string, make it NULL (None).
            if not len(room):
                room = None
            # Change "Cancelled Cancelled" to just "Cancelled".
            if days == "Cancelled Cancelled":
                days = days[:9]

            # Insert into the table.
            # This method prevents SQL-injection.
            # https://www.psycopg.org/docs/sql.html#module-usage
            if verbose:
                print(
                    f"Inserting class:\n"
                    f"- Code: {code}\n"
                    f"- Name: {name}\n"
                    f"- Number: {number}\n"
                    f"- Instructor(s): {instructor}\n"
                    f"- Room: {room}\n"
                    f"- Days: {days}"
                )
            cursor.execute(
                sql.SQL(
                    '''
                    INSERT INTO {}(code, name, number, instructor, room, days)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    '''
                ).format(sql.Identifier(table.lower())),
                (code, name, number, instructor, room, days)
            )
            if verbose:
                print(
                    f"Successfully added {code}: {name}."
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
        description="Loads data from a csv file into a table in the database.",
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
        help="the csv file that will be parsed"
    )
    parser.add_argument(
        "tbl",
        help="the table in the database that will hold the data"
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
        # Load csv file and upload its data to the database.
        conn.autocommit = True  # Auto-commit transactions.
        if args.verbose:
            print(
                f"Account '{args.user}' connected to host '{args.host}'.\n"
                f"Loading data from '{args.file}' into table '{args.tbl}'...\n"
            )
        with conn.cursor() as cur:
            parse_csv(cur, args.file, args.tbl, args.verbose)
        if args.verbose:
            print(
                "Inserted all data from csv file.\n"
            )
        conn.close()
    return


if __name__ == "__main__":
    main()
