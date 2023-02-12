#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Queries class data in the database.
"""

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


def view_table(cursor, table: str, limit: int, offset: int) -> None:
    """
    Prints table data to ``stdout``.

    Args:
        cursor: A database cursor from a connection.
        table: The table in the database to query.
        limit: The number of rows to query.
        offset: The offset to apply to the query.
    """
    # Select all columns from the table.
    # This method prevents SQL-injection.
    # https://www.psycopg.org/docs/sql.html#module-usage
    cursor.execute(
        sql.SQL(
            '''
            SELECT * FROM {}
            ORDER BY code
            LIMIT %s
            OFFSET %s
            '''
        ).format(sql.Identifier(table.lower())),
        (
            limit,
            offset,
        )
    )

    # Once retrieved, unpack and print all cursor information.
    print(f"=== Table data for '{table}' ===")
    for class_info in cursor:
        number, code, name, inst, meetings, mode, timestamp = class_info
        print(
            f"= {code}: {name}\n"
            f"--- Number: {number}\n"
            f"--- Mode: {mode}\n"
            f"--- Instructor(s): {inst}\n"
            f"--- Meetings: {meetings}\n"
            f"--- Entry last updated: {timestamp} UTC",
        )
    return


def main() -> None:
    """
    Queries class data in the database.
    """
    # Program defaults.
    db_host = "cfdb.cr6zou4a0wxq.us-west-1.rds.amazonaws.com"
    db_name = "cfdb"
    db_port = "5432"

    # Parse command-line arguments.
    parser = ap.ArgumentParser(
        description="Queries class data in the database.",
        epilog="Returned information is sorted by code.",
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
        "tbl",
        help="the table in the database to query"
    )
    parser.add_argument(
        "lim",
        help="the max number of rows to query",
        type=int
    )
    parser.add_argument(
        "off",
        help="the offset of the rows to query",
        type=int
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
        # Query the user's table.
        with conn.cursor() as cur:
            view_table(cur, args.tbl, args.lim, args.off)
        conn.close()
    return


if __name__ == "__main__":
    main()
