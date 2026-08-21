import re
import urllib.request
from html import unescape


RRB_URL = "https://www.rrbcdg.gov.in/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 RozgarSathiBot/1.0"
}


def fetch_rrb():

    try:

        request = urllib.request.Request(
            RRB_URL,
            headers=HEADERS
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            return response.read().decode(
                "utf-8",
                errors="ignore"
            )

    except Exception as error:

        print("RRB source error:", error)

        return ""


def clean_html(text):

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = unescape(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def absolute_url(url):

    url = url.strip()

    if url.startswith("http://"):
        return url

    if url.startswith("https://"):
        return url

    if url.startswith("/"):

        return (
            "https://www.rrbcdg.gov.in"
            + url
        )

    return (
        "https://www.rrbcdg.gov.in/"
        + url
    )


def get_rrb_notices():

    html = fetch_rrb()

    if not html:

        return []


    notices = []


    pattern = re.compile(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
        r'(.*?)'
        r'</a>',
        re.I | re.S
    )


    matches = pattern.findall(
        html
    )


    keywords = [

        "CEN",

        "Recruitment",

        "recruitment",

        "Vacancy",

        "vacancy",

        "Technician",

        "NTPC",

        "ALP",

        "Group D",

        "Level",

        "JE",

        "Junior Engineer",

        "Paramedical",

        "Apprentice"

    ]


    for url, title in matches:

        title = clean_html(
            title
        )


        if not title:

            continue


        if not any(
            keyword in title
            for keyword in keywords
        ):

            continue


        url = absolute_url(
            url
        )


        notices.append({

            "title": title,

            "url": url

        })


    # Duplicate notices हटाएँ

    unique = {}

    for notice in notices:

        unique[
            notice["url"]
        ] = notice


    return list(
        unique.values()
    )


def get_jobs():

    notices = get_rrb_notices()

    jobs = []


    for notice in notices:

        jobs.append({

            "id":
            "RRB-" +
            str(
                abs(
                    hash(
                        notice["url"]
                    )
                )
            ),

            "title":
            "Railway " +
            notice["title"],

            "category":
            "Government",

            "qualification":
            "Official notification के अनुसार",

            "posts":
            "Official notification के अनुसार",

            "lastDate":
            "",

            "page":
            notice["url"]

        })


    return jobs


if __name__ == "__main__":

    jobs = get_jobs()


    print("")
    print(
        "RRB parser result:"
    )


    for job in jobs:

        print(
            "-",
            job["title"]
        )


    print(
        "Total:",
        len(jobs)
    )
