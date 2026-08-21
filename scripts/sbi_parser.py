import re
import urllib.request
from html import unescape


SBI_URL = "https://sbi.bank.in/web/careers/current-openings"


def fetch_sbi():

    try:

        request = urllib.request.Request(
            SBI_URL,
            headers={
                "User-Agent": "Mozilla/5.0"
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

        print("SBI error:", error)

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


def get_sbi_recruitment_notices():

    html = fetch_sbi()

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

        "recruitment",

        "engagement",

        "junior associate",

        "probationary officer",

        "specialist cadre",

        "officer",

        "apprentice",

        "vacancies"

    ]


    for url, title in matches:

        title = clean_html(
            title
        )


        if not title:

            continue


        title_lower = title.lower()


        if not any(
            word in title_lower
            for word in keywords
        ):

            continue


        if url.startswith("/"):

            url = (
                "https://sbi.bank.in"
                +
                url
            )


        if not url.startswith("http"):

            continue


        notices.append({

            "title": title,

            "url": url

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
        get_sbi_recruitment_notices()
    )


    jobs = []


    for notice in notices:

        jobs.append({

            "id":
            "SBI-" +
            str(
                abs(
                    hash(
                        notice["url"]
                    )
                )
            ),

            "title":
            "SBI " +
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
        "SBI parser result:"
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
