import re
import urllib.request
from html import unescape


SSC_URL = "https://ssc.gov.in/"


def fetch_ssc():

    try:

        request = urllib.request.Request(
            SSC_URL,
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

        print("SSC error:", error)

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


def get_ssc_recruitment_notices():

    html = fetch_ssc()

    if not html:

        return []


    notices = []


    # SSC page पर recruitment-related
    # links खोजने की कोशिश

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

        "examination",

        "selection post",

        "combined graduate",

        "higher secondary",

        "stenographer",

        "junior engineer",

        "constable",

        "sub inspector",

        "multi tasking",

        "vacancy"

    ]


    for url, title in matches:

        title = clean_html(
            title
        )


        title_lower = title.lower()


        if not title:

            continue


        if not any(
            word in title_lower
            for word in keywords
        ):

            continue


        if url.startswith("/"):

            url = (
                "https://ssc.gov.in"
                +
                url
            )


        if not url.startswith("http"):

            continue


        notices.append({

            "title": title,

            "url": url

        })


    # duplicate हटाएँ

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
        get_ssc_recruitment_notices()
    )


    jobs = []


    for notice in notices:

        jobs.append({

            "id":
            "SSC-" +
            str(
                abs(
                    hash(
                        notice["url"]
                    )
                )
            ),

            "title":
            "SSC " +
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
        "SSC parser result:"
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
