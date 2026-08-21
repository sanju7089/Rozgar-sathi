import re
import json
import urllib.request
from datetime import datetime

JOBS_FILE = "jobs-data.js"
CLOSED_FILE = "closed-jobs-data.js"

# =========================================================
# ROZGAR SATHI - AUTOMATIC JOB DATABASE
# =========================================================

# अभी verified Government sources का base setup
# आगे इसी list में Railway, India Post, Defence आदि जोड़ेंगे।

GOVERNMENT_SOURCES = [
    {
        "name": "SSC",
        "category": "Government",
        "url": "https://ssc.gov.in/"
    },
    {
        "name": "UPSC",
        "category": "Government",
        "url": "https://www.upsc.gov.in/recruitment/recruitment-advertisement"
    },
    {
        "name": "IBPS",
        "category": "Banking",
        "url": "https://www.ibps.in/"
    }
]


def today():
    return datetime.now().date()


def parse_date(value):

    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y"
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                value.strip(),
                fmt
            ).date()

        except ValueError:
            pass

    return None


def clean(value):

    value = str(value or "")

    value = value.replace(
        "\n",
        " "
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def escape_js(value):

    value = clean(value)

    return (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )


def job_to_js(job):

    return f'''{{
  id:"{escape_js(job["id"])}",
  title:"{escape_js(job["title"])}",
  category:"{escape_js(job["category"])}",
  qualification:"{escape_js(job["qualification"])}",
  posts:"{escape_js(job["posts"])}",
  lastDate:"{escape_js(job["lastDate"])}",
  page:"{escape_js(job["page"])}"
}}'''


def read_existing_jobs():

    try:

        with open(
            JOBS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

    except FileNotFoundError:

        return []


    pattern = re.compile(
        r'\{\s*'
        r'id:"([^"]*)",\s*'
        r'title:"([^"]*)",\s*'
        r'category:"([^"]*)",\s*'
        r'qualification:"([^"]*)",\s*'
        r'posts:"([^"]*)",\s*'
        r'lastDate:"([^"]*)",\s*'
        r'page:"([^"]*)"\s*'
        r'\}',
        re.MULTILINE
    )


    matches = pattern.findall(
        content
    )


    jobs = []


    for item in matches:

        jobs.append({
            "id": item[0],
            "title": item[1],
            "category": item[2],
            "qualification": item[3],
            "posts": item[4],
            "lastDate": item[5],
            "page": item[6]
        })


    return jobs


def fetch_page(url):

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "RozgarSathiBot/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            return response.read().decode(
                "utf-8",
                errors="ignore"
            )

    except Exception as error:

        print(
            "Source error:",
            url,
            error
        )

        return ""


def create_source_job(source):

    """
    यह source record है।

    जब किसी source का notification parser
    तैयार होगा, तो इसी structure में
    वास्तविक vacancies आएंगी।
    """

    return {
        "id":
        "SOURCE-" +
        source["name"].upper(),

        "title":
        source["name"] +
        " Recruitment Updates",

        "category":
        source["category"],

        "qualification":
        "Official notification के अनुसार",

        "posts":
        "Official notification के अनुसार",

        "lastDate":
        "",

        "page":
        source["url"]
    }


def collect_government_sources():

    jobs = []

    for source in GOVERNMENT_SOURCES:

        print(
            "Checking:",
            source["name"]
        )

        page = fetch_page(
            source["url"]
        )

        if page:

            print(
                source["name"],
                "source available"
            )

        # IMPORTANT:
        # बिना notification details पढ़े
        # fake vacancy generate नहीं की जाएगी।

    return jobs


def split_active_closed(jobs):

    active = []

    closed = []

    current_date = today()


    for job in jobs:

        expiry = parse_date(
            job.get("lastDate", "")
        )


        if expiry is None:

            active.append(job)

            continue


        if expiry < current_date:

            closed.append(job)

        else:

            active.append(job)


    return active, closed


def write_database(
    filename,
    variable,
    jobs
):

    output = (
        "const " +
        variable +
        " = [\n\n"
    )


    output += ",\n\n".join(
        job_to_js(job)
        for job in jobs
    )


    output += "\n\n];\n"


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(output)


def remove_duplicate_jobs(jobs):

    unique = {}

    for job in jobs:

        job_id = job.get(
            "id",
            ""
        )

        if not job_id:

            continue

        unique[job_id] = job


    return list(
        unique.values()
    )


def update_jobs():

    print("")
    print("=" * 45)
    print("ROZGAR SATHI AUTOMATIC JOB SYSTEM")
    print("=" * 45)


    existing_jobs = read_existing_jobs()


    print(
        "Existing jobs:",
        len(existing_jobs)
    )


    # Government sources check
    new_jobs = collect_government_sources()


    # Existing + newly collected
    all_jobs = (
        existing_jobs +
        new_jobs
    )


    all_jobs = remove_duplicate_jobs(
        all_jobs
    )


    active_jobs, closed_jobs = (
        split_active_closed(
            all_jobs
        )
    )


    write_database(
        JOBS_FILE,
        "jobs",
        active_jobs
    )


    write_database(
        CLOSED_FILE,
        "closedJobs",
        closed_jobs
    )


    print("")
    print(
        "Total jobs:",
        len(all_jobs)
    )

    print(
        "Active jobs:",
        len(active_jobs)
    )

    print(
        "Closed jobs:",
        len(closed_jobs)
    )

    print("=" * 45)


if __name__ == "__main__":

    update_jobs()
