#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapes the UCSC Class Search for class information.
"""

import datetime
import sys

import argparse as ap

from http import HTTPStatus
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

# Check if the requests module is installed on the system,
# as it is needed to send HTTP requests to the server.
try:
    import requests as req
except ImportError:
    print(
        "'requests' module not found. "
        "Install the 'requests' module through PIP.",
        file=sys.stderr
    )
    sys.exit(1)


def scrape_class_data(file: str, term: int, verbose: bool = False) -> None:
    """
    Scrapes class data for a particular term from the UCSC Class Search
    and saves it in a JSON file.

    Args:
        file: The JSON file to save the scraped data to.
        term: The term to scrape class data from.
        Expects an integer representing the term used by the Class Search.
        verbose: Verbose mode; prints what is happening to ``stdout``.

    Raises:
        RuntimeError: If an HTTP POST request fails.
    """
    # NOTE: Term-checking should be done before this function is called.

    # All the information required to send an HTTP POST request.
    # The payload and request headers will be sent to the URL.
    url = "https://pisa.ucsc.edu/class_search/index.php"
    payload = {
        'action': 'update_segment',
        'binds[:term]': term,
        'binds[:reg_status]': 'all',
        'binds[:subject]': '',
        'binds[:catalog_nbr_op]': '=',
        'binds[:catalog_nbr]': '',
        'binds[:title]': '',
        'binds[:instr_name_op]': '=',
        'binds[:instructor]': '',
        'binds[:ge]': '',
        'binds[:crse_units_op]': '=',
        'binds[:crse_units_from]': '',
        'binds[:crse_units_to]': '',
        'binds[:crse_units_exact]': '',
        'binds[:days]': '',
        'binds[:times]': '',
        'binds[:acad_career]': '',
        'binds[:asynch]': 'A',
        'binds[:hybrid]': 'H',
        'binds[:synch]': 'S',
        'binds[:person]': 'P',
        'rec_start': 0,
        'rec_dur': 100
    }
    headers = {
        'Accept': 'text/html',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Length': str(len(urlencode(payload))),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'pisa.ucsc.edu',
        'Origin': 'https://pisa.ucsc.edu',
        'Referer': 'https://pisa.ucsc.edu/class_search/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1'
    }

    # Open the file.
    with open(file, "w") as f:
        # To ensure all data has been scraped for a particular term,
        # keep sending POST requests until all pages have been loaded.
        # Manually create the JSON file as the program parses.
        print(
            "{\n"
            "    \"classes\": [\n",
            end="",
            file=f
        )

        # Get current Pacific time.
        time = datetime.datetime.now(
            ZoneInfo("UTC")
        ).strftime("%Y-%m-%d %H:%M:%S")

        keep_requesting = True
        require_comma = False  # Needed to prevent trailing commas.
        while keep_requesting:
            # Send an HTTP POST request to the URL and check its response.
            res = req.post(url, data=payload, headers=headers)
            if res.status_code != HTTPStatus.OK.value:
                raise RuntimeError(
                    f"POST request returned {res.status_code} {res.reason}"
                )

            # Information for each class is ordered the following way:
            # Line-by-line:
            # - Code and name
            # - Number
            # - Instructor(s)
            #
            # As a repeating pair:
            # - Location
            # - Day(s) and time(s)
            #
            # Back to line-by-line:
            # - Mode
            for line_bytes in res.iter_lines():
                ln = line_bytes.decode('utf-8')

                # Current number of classes displayed.
                # Used to determine when to stop sending requests.
                if "</b> - <b>" in ln:
                    # Get the total number of classes.
                    s = ""
                    for i in range(ln.rfind("</b>") - 1, 0, -1):
                        if ln[i] == ">":
                            break
                        s += ln[i]
                    total_classes = int(s[::-1])

                    # Get the current number of classes displayed.
                    s = ""
                    for i in range(
                        ln.rfind("</b>", 0, ln.rfind("</b>")) - 1,
                        0,
                        -1
                    ):
                        if ln[i] == ">":
                            break
                        s += ln[i]
                    current_classes = int(s[::-1])

                    if verbose:
                        print(
                            f"Scraping progress: "
                            f"{current_classes} / {total_classes}..."
                        )

                    # If on the final page, stop sending requests.
                    if current_classes >= total_classes:
                        keep_requesting = False
                    continue

                # Class code and name.
                if "<div class=\"panel-heading panel-heading-custom\">" in ln:
                    s = ""
                    for i in range(ln.rfind("</a>") - 1, 0, -1):
                        if ln[i] == ">":
                            break
                        s += ln[i]
                    code, name = s[::-1].split("&nbsp;&nbsp;&nbsp;")
                    code = code.replace(" ", "")
                    name = name.replace("&amp;", "&")

                    # Print to file.
                    print(
                        "        {\n"
                        "            \"code\": \"" + code + "\",\n"
                        "            \"name\": \"" + name + "\",\n",
                        end="",
                        file=f
                    )
                    continue

                # Class number.
                if "Class Number:" in ln:
                    s = ""
                    for i in range(ln.rfind("</a>") - 1, 0, -1):
                        if ln[i] == ">":
                            break
                        s += ln[i]
                    number = s[::-1]

                    # Print to file.
                    print(
                        "            \"number\": {},\n"
                        .format(number),
                        end="",
                        file=f
                    )
                    continue

                # Instructor.
                if "Instructor:" in ln:
                    s = ""
                    for i in range(ln.rfind("</div>") - 1, 0, -1):
                        if ln[i] == "/":
                            break
                        s += ln[i]
                    s = s[:-3]
                    instructors = s[::-1].split("<br>")

                    # Print to file.
                    print(
                        "            \"instructors\": [\n",
                        end="",
                        file=f
                    )
                    for index, instructor in enumerate(instructors):
                        print(
                            "                \"{}\""
                            .format(instructor),
                            end="",
                            file=f
                        )
                        if index == len(instructors) - 1:
                            print(
                                "\n            ],\n"
                                "            \"meetings\": [\n",
                                end="",
                                file=f
                            )
                            break
                        else:
                            print(
                                ",\n",
                                end="",
                                file=f
                            )
                    continue

                # Location.
                if "Location:" in ln:
                    s = ""
                    for i in range(ln.rfind("</div>") - 1, 0, -1):
                        if ln[i] == ">":
                            break
                        s += ln[i]
                    location = s[::-1].strip(" ")

                    # If just an identifier like SEM, STU, etc.,
                    # make it the empty string.
                    # Otherwise, strip this identifier.
                    if len(location) == 3:
                        location = ""
                    else:
                        location = location[5:]

                    # Print to file.
                    # If there are multiple meetings, add a comma.
                    if require_comma:
                        print(
                            ",\n",
                            end="",
                            file=f
                        )
                    print(
                        "                [\n"
                        "                    \"{}\",\n"
                        .format(location),
                        end="",
                        file=f
                    )
                    continue

                # Day and time.
                if "Day and Time:" in ln:
                    s = ""
                    for i in range(ln.rfind("</div>") - 1, 0, -1):
                        # if line[i] == ">":
                        #     break
                        if ln[i] == "/":
                            break
                        s += ln[i]
                    s = s[:-2]
                    times = s[::-1].strip(
                        " "
                    ).replace(
                        "&nbsp;", ""
                    ).replace(
                        "Cancelled Cancelled",
                        "Cancelled"
                    ).split(
                        "<br>"
                    )

                    # Print to file.
                    if len(times) == 1:
                        print(
                            "                    \"{}\"\n"
                            "                ]"
                            .format(times[0]),
                            end="",
                            file=f
                        )
                    else:
                        print(
                            "                    \"{}\",\n"
                            "                    \"{}\"\n"
                            "                ]"
                            .format(times[0], times[1]),
                            end="",
                            file=f
                        )

                    # In case more meeting times are present.
                    require_comma = True
                    continue

                # Mode.
                if "Instruction Mode:" in ln:
                    s = ""
                    for i in range(ln.rfind("</b>") - 1, 0, -1):
                        if ln[i] == ">":
                            break
                        s += ln[i]
                    mode = s[::-1]

                    # Print to file.
                    # Fix formatting.
                    if require_comma:
                        require_comma = False
                        print(
                            "\n",
                            end="",
                            file=f
                        )
                    print(
                        "            ],\n"
                        "            \"mode\": \"" + mode + "\",\n",
                        end="",
                        file=f
                    )

                    # Since this is guaranteed to be the last item,
                    # also add a key for last updated time.
                    print(
                        "            \"last_updated\": \"" + time + "\"\n"
                        "        },\n",
                        end="",
                        file=f
                    )
                    continue

            # For subsequent POST requests, alter the payload accordingly.
            # Adding 100 to 'rec_start' gets the next page if 'action' is next.
            # In both the initial request and the first next request, however,
            # 'rec_start' should still be 0.
            payload['rec_start'] += 100
            if payload['action'] != "next":
                payload['action'] = "next"
                payload['rec_start'] = 0

        print(
            "    ]\n"
            "}",
            file=f
        )

    # Once done adding classes, reopen the file in binary mode.
    # This is done to literally just remove one comma.
    with open(file, "r+b") as f:
        f.seek(-10, 2)
        f.write(b" ")
    return


def main() -> None:
    """
    Scrapes the UCSC Class Search for class information.
    """
    # Parse command-line arguments.
    parser = ap.ArgumentParser(
        description="Scrapes the UCSC Class Search and saves it as JSON.",
        formatter_class=ap.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "file",
        help="the JSON file that will store the data",
    )
    parser.add_argument(
        "term",
        help="the term to scrape class data from, formatted as <term><year>"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="verbose mode"
    )
    args = parser.parse_args()

    # To prevent sending garbage, check if term is supported.
    # Afterwards, send the POST request.
    valid_terms = {
        "spring2023": 2232,
        "winter2023": 2230,
        "fall2022": 2228
    }
    if args.term.lower() in valid_terms:
        if args.verbose:
            print(
                f"Scraping data from term '{args.term.capitalize()}' "
                f"into file '{args.file}'...\n"
            )
        scrape_class_data(args.file, valid_terms[args.term], args.verbose)
        if args.verbose:
            print(
                "\nScraping complete.\n"
            )
    else:
        raise ValueError(f"term '{args.term}' unsupported")
    return


if __name__ == "__main__":
    main()
