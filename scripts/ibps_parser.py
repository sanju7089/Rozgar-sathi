import re
import urllib.request
from html import unescape


IBPS_URL = "https://www.ibps.in/"


def fetch_ibps():

    try:

        request = urllib.request.Request(
            IBPS_URL,
            headers={
                "User-Agent":
                "Mozilla/5.0 RozgarSathiBot/1.0"
            }
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

        print(
            "IBPS error:",
            error
        )

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
            "https://www.ibps.in"
            + url
        )

    return (
        "https://www.ibps.in/"
        + url
    )


def get_ibps_notices():

    html = fetch_ibps()

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

        "CRP",

        "Recruitment",

        "recruitment",

        "Vacancy",

        "vacancy",

        "PO",

        "MT",

        "Clerk",

        "Office Assistant",

        "Officer",

        "Specialist",

        "RRB",

        "Probationary"

    ]


    for url, title in matches:

        title = clean_html(
            title
        )


        if not title:

            continue


        if not any(
            keyword.lower()
            in title.lower()
            for keyword in keywords
        ):

            continue


        url = absolute_url(
            url
        )


        notices.append({

            "title":
            title,

            "url":
            url

        })


    unique = {}


    for notice in notices:

        unique[
            notice["url"]
        ] = notice


    return list(
        unique.values()
    )


def get_jobs():

    notices = get_ibps_notices()

    jobs = []


    for notice in notices:

        jobs.append({

            "id":
            "IBPS-" +
            str(
                abs(
                    hash(
                        notice["url"]
                    )
                )
            ),

            "title":
            "IBPS " +
            notice["title"],

            "category":
            "Banking",

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
        "IBPS parser result:"
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
