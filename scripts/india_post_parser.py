import re
import urllib.request
from html import unescape


INDIA_POST_URL = "https://indiapostgdsonline.gov.in/"


def fetch_india_post():

    try:

        request = urllib.request.Request(
            INDIA_POST_URL,
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
            "India Post error:",
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
            "https://indiapostgdsonline.gov.in"
            + url
        )

    return (
        INDIA_POST_URL
        + url
    )


def get_india_post_notices():

    html = fetch_india_post()

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

        "GDS",

        "Recruitment",

        "recruitment",

        "Vacancy",

        "vacancy",

        "Schedule",

        "Notification",

        "Result",

        "Engagement",

        "Post Office"

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

    notices = (
        get_india_post_notices()
    )


    jobs = []


    for notice in notices:

        jobs.append({

            "id":
            "INDIAPOST-" +
            str(
                abs(
                    hash(
                        notice["url"]
                    )
                )
            ),

            "title":
            "India Post " +
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
        "India Post parser result:"
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
