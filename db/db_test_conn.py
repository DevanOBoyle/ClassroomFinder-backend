#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checks if a given account can connect to a database.
"""

import sys

import argparse as ap

# Check if the psycopg2 module is installed on the system,
# as it is needed to connect to the PostgreSQL database.
try:
    import psycopg2
except ImportError:
    print(
        "'psycopg2' module not found. "
        "Install the 'psycopg2-binary' module through PIP.",
        file=sys.stderr
    )
    sys.exit(1)


def main() -> None:
    """
    Checks if a given account can connect to a database.
    """
    # Program defaults.
    db_host = "cfdb.cr6zou4a0wxq.us-west-1.rds.amazonaws.com"
    db_name = "cfdb"
    db_port = "5432"

    # Parse command-line arguments.
    parser = ap.ArgumentParser(
        description="Check if connecting to the database is successful.",
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
        print(
            f"Account '{args.user}' connected to host '{args.host}'.\n"
        )
        conn.close()
    return


if __name__ == "__main__":
    main()
