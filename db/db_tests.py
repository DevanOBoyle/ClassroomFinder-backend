#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runs some tests on the database.
"""
#
# IMPORTS
#


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


#
# CLASSES AND FUNCTIONS
#


class UnitTestSuite:
    """
    A unit test suite containing various database tests.
    """
    def __init__(
        self,
        user: str,
        pswd: str,
        name: str,
        host: str,
        port: str
    ) -> None:
        self.user = user
        self.pswd = pswd
        self.name = name
        self.host = host
        self.port = port
        self.tests = list(filter(lambda x: x.startswith("test"), dir(self)))
        return

    def run_all_tests(self, stop_on_fail: bool = False) -> None:
        """
        Runs all defined tests in the testing suite.

        Args:
            stop_on_fail: If encountering a failed test stops testing.
        """
        print("Running all tests...")
        passed = 0
        failed = 0
        for num, test in enumerate(self.tests, 1):
            print(f"- Running Test #{num:02d} - '{test}': ", end="")
            if getattr(self, test)():
                print("PASSED")
                passed += 1
            else:
                print("FAILED")
                failed += 1
                if stop_on_fail:
                    print("Testing stopped due to failure.")
                    break
        if failed == 0:
            print(
                f"Results: All tests passed "
                f"({passed} / {passed + failed})."
            )
        else:
            print(
                f"Results: {passed} passed, {failed} failed "
                f"({passed} / {passed + failed})."
            )
        return

    def _before_test(self) -> None:
        """
        Establishes a connection to the database.
        This is run before every test.
        """
        try:
            self.conn = psycopg2.connect(
                database=self.name,
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.pswd,
            )
        except psycopg2.OperationalError:
            self.conn = None
        return

    def _after_test(self) -> None:
        """
        Closes a connection to the database.
        This is run after every test.
        """
        if self.conn:
            self.conn.close()
        return

    def test_01_check_connectivity(self) -> bool:
        """
        Tests if a connection can be made to the database.
        """
        # If the connection is not None, then the test passed.
        self._before_test()
        ret = False

        if self.conn:
            ret = True

        self._after_test()
        return ret

    def test_02_query_classes(self) -> bool:
        """
        Tests if a 'classes_<term>' table can be queried.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT code FROM classes_fall2022
                    WHERE name = 'Math Methods I'
                    """
                )
                if cur.fetchone()[0] == "AM10-01":
                    ret = True

        self._after_test()
        return ret

    def test_03_query_instructors(self) -> bool:
        """
        Tests if a 'instructors_<term>' table can be queried.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT instructor FROM instructors_fall2022
                    WHERE class_number = 10034
                    """
                )
                if cur.fetchone()[0] == "Gong,Q.":
                    ret = True

        self._after_test()
        return ret

    def test_04_query_meetings(self) -> bool:
        """
        Tests if a 'meetings_<term>' table can be queried.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT meeting_place, meeting_time FROM meetings_fall2022
                    WHERE class_number = 25222
                    """
                )
                if cur.fetchone() == ("Soc Sci 1 414", "Th 09:45AM-01:15PM"):
                    ret = True

        self._after_test()
        return ret

    def test_05_query_buildings(self) -> bool:
        """
        Tests if the 'buildings' table can be queried.
        """
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT name FROM buildings
                    WHERE number = 23
                    """
                )
                if cur.fetchone()[0] == "McHenry Library":
                    ret = True

        self._after_test()
        return ret

    def test_06_query_rooms(self) -> bool:
        """
        Tests if the 'rooms' table can be queried.
        """
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT number, floor, capacity FROM rooms
                    WHERE name = 'J Bask Aud 101'
                    """
                )
                if cur.fetchone() == ("101", 1, 207):
                    ret = True

        self._after_test()
        return ret

    def test_07_query_join_buildings_rooms(self) -> bool:
        """
        Tests if a join between 'buildings' and 'rooms'
        yields accurate information.
        """
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT b.name, r.number, r.floor
                    FROM rooms AS r
                    JOIN buildings AS b ON b.number = r.building_number
                    WHERE r.name = 'Thim Lecture 003'
                    """
                )
                if cur.fetchone() == ("Thimann Lecture Hall", "003", 1):
                    ret = True

        self._after_test()
        return ret

    def test_08_query_join_classes_instructors(self) -> bool:
        """
        Tests if a join between 'classes_<term>' and 'instructors_<term>'
        yields accurate information.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.code, i.instructor
                    FROM classes_fall2022 AS c
                    JOIN instructors_fall2022 AS i ON c.number = i.class_number
                    WHERE c.name = 'Math Methods III'
                    """
                )
                if cur.fetchone() == ("AM100-01", "Wang,H."):
                    ret = True

        self._after_test()
        return ret

    def test_09_query_join_classes_meetings(self) -> bool:
        """
        Tests if a join between 'classes_<term>' and 'meetings_<term>'
        yields accurate information.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.code, m.meeting_place
                    FROM classes_fall2022 AS c
                    JOIN meetings_fall2022 AS m ON c.number = m.class_number
                    WHERE c.name = 'Math Methods III'
                    """
                )
                if cur.fetchone() == ("AM100-01", "Steven Acad 150"):
                    ret = True

        self._after_test()
        return ret

    def test_10_query_join_all_class_info(self) -> bool:
        """
        Tests if a join among 'classes_<term>', 'meetings_<term>',
        and 'instructors_<term>' yields accurate information.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.code, i.instructor, m.meeting_place
                    FROM classes_fall2022 AS c
                    JOIN meetings_fall2022 AS m ON c.number = m.class_number
                    JOIN instructors_fall2022 AS i ON c.number = i.class_number
                    WHERE c.name = 'Math Methods III'
                    """
                )
                if cur.fetchone() == ("AM100-01", "Wang,H.", "Steven Acad 150"):
                    ret = True

        self._after_test()
        return ret

    def test_11_query_join_meetings_rooms(self) -> bool:
        """
        Tests if a join between 'meetings_<term>' and 'rooms'
        yields accurate information.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.name, r.floor, m.meeting_time
                    FROM rooms AS r
                    JOIN meetings_fall2022 AS m ON r.name = m.meeting_place
                    WHERE m.meeting_place = 'J Bask Aud 101'
                    """
                )

                # Since this yields many results, only get the 2nd one.
                if cur.fetchall()[1] == ("J Bask Aud 101", 1, "M 08:00AM-09:05AM"):
                    ret = True

        self._after_test()
        return ret

    def test_12_query_join_meetings_rooms_buildings(self) -> bool:
        """
        Tests if a join among 'meetings_<term>', 'rooms',
        and 'buildings' yields accurate information.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT b.name, r.floor, m.meeting_time
                    FROM rooms AS r
                    JOIN meetings_fall2022 AS m ON r.name = m.meeting_place
                    JOIN buildings AS b ON b.number = r.building_number
                    WHERE m.meeting_place = 'J Bask Aud 101'
                    """
                )

                # Since this yields many results, only get the 2nd one.
                if cur.fetchall()[1] == ("Jack Baskin Engineering Auditorium", 1, "M 08:00AM-09:05AM"):
                    ret = True

        self._after_test()
        return ret

    def test_13_query_join_everything(self) -> bool:
        """
        Tests if a join among 'classes_<term>', 'instructors_<term>',
        'meetings_<term>', 'buildings', and 'rooms' yields accurate
        information.
        """
        # Use the Fall 2022 term, as that quarter has already passed.
        self._before_test()
        ret = False

        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT b.name, r.number, c.code, i.instructor, m.meeting_time
                    FROM classes_fall2022 AS c
                    JOIN instructors_fall2022 AS i ON c.number = i.class_number
                    JOIN meetings_fall2022 AS m ON c.number = m.class_number
                    JOIN rooms AS r ON m.meeting_place = r.name
                    JOIN buildings AS b ON r.building_number = b.number
                    WHERE c.name = 'Intro Software Eng'
                    """
                )

                if cur.fetchone() == \
                    (
                        "Jack Baskin Engineering Building",
                        "152",
                        "CSE115A-01",
                        "Jullig,R.K.",
                        "MWF 08:00AM-09:05AM"
                    ):
                    ret = True

        self._after_test()
        return ret


def main() -> None:
    # Program defaults.
    db_host = "cfdb.cr6zou4a0wxq.us-west-1.rds.amazonaws.com"
    db_name = "cfdb"
    db_port = "5432"

    # Parse command-line arguments.
    parser = ap.ArgumentParser(
        description="Perform tests on the database.",
        epilog="Test information is printed to stdout."
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
        "-s",
        "--stop",
        action="store_true",
        help="stops testing upon failure"
    )
    args = parser.parse_args()

    UnitTestSuite(
        args.user,
        args.pswd,
        db_name,
        db_host,
        db_port
    ).run_all_tests(args.stop)
    return


if __name__ == "__main__":
    main()
