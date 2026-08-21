import re
import urllib.request
from html import unescape


UPSC_URL = "https://www.upsc.gov.in/recruitment/recruitment-advertisement"


def fetch_upsc():

    try:

        request = urllib.request.Request(
            UPSC_URL,
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
            "UPSC error:",
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
            "https://www.upsc.gov.in"
            + url
        )

    return (
        "https://www.upsc.gov.in/"
        + url
    )


def get_upsc_notices():

    html = fetch_upsc()

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

        "Advertisement",

        "Recruitment",

        "recruitment",

        "Engineering Services",

        "Civil Services",

        "Combined Defence",

        "National Defence",

        "NDA",

        "CDS",

        "CMS",

        "EPFO",

        "Assistant",

        "Officer",

        "Scientist",

        "Specialist"

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

    notices = get_upsc_notices()

    jobs = []


    for notice in notices:

        jobs.append({

            "id":
            "UPSC-" +
            str(
                abs(
                    hash(
                        notice["url"]
                    )
                )
            ),

            "title":
            "UPSC " +
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
        "UPSC parser result:"
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
