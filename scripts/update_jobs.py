import re
import json
from datetime import datetime
from urllib.request import Request, urlopen

JOBS_FILE = "jobs-data.js"
CLOSED_FILE = "closed-jobs-data.js"
SOURCES_FILE = "job-sources.json"


def today_date():
    return datetime.now().date()


def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def job_to_js(job):
    return f'''{{
  id:"{job[0]}",
  title:"{job[1]}",
  category:"{job[2]}",
  qualification:"{job[3]}",
  posts:"{job[4]}",
  lastDate:"{job[5]}",
  page:"{job[6]}"
}}'''


def read_jobs(filename, variable_name):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return []

    pattern = re.compile(
        r'\{\s*'
        r'id:"([^"]+)",\s*'
        r'title:"([^"]+)",\s*'
        r'category:"([^"]+)",\s*'
        r'qualification:"([^"]+)",\s*'
        r'posts:"([^"]+)",\s*'
        r'lastDate:"([^"]+)",\s*'
        r'page:"([^"]+)"\s*'
        r'\}',
        re.MULTILINE
    )

    return pattern.findall(content)


def write_jobs(filename, variable_name, jobs):

    output = f"const {variable_name} = [\n\n"

    if jobs:
        output += ",\n\n".join(
            job_to_js(job) for job in jobs
        )

    output += "\n\n];\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)


def load_sources():

    try:
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("sources", [])

    except Exception as error:
        print("Source file error:", error)
        return []


def check_source(url):

    try:

        request = Request(
            url,
            headers={
                "User-Agent": "Rozgar-Sathi-Bot/1.0"
            }
        )

        with urlopen(
            request,
            timeout=20
        ) as response:

            html = response.read().decode(
                "utf-8",
                errors="ignore"
            )

            return len(html) > 0

    except Exception as error:

        print(
            "Source check failed:",
            url,
            error
        )

        return False


def remove_expired(jobs, closed_jobs):

    today = today_date()

    active = []
    closed = list(closed_jobs)

    existing_closed_ids = {
        job[0] for job in closed
    }

    for job in jobs:

        try:

            expiry_date = parse_date(
                job[5]
            )

        except ValueError:

            active.append(job)
            continue

        if expiry_date < today:

            if job[0] not in existing_closed_ids:

                closed.append(job)

                existing_closed_ids.add(
                    job[0]
                )

        else:

            active.append(job)

    return active, closed


def check_sources():

    sources = load_sources()

    print("--------------------------------")
    print("CHECKING OFFICIAL JOB SOURCES")
    print("--------------------------------")

    working = 0

    for source in sources:

        name = source.get(
            "name",
            "Unknown"
        )

        url = source.get(
            "url",
            ""
        )

        print(
            f"Checking: {name}"
        )

        if not url:
            continue

        if check_source(url):

            print("OK:", url)

            working += 1

        else:

            print(
                "Could not access:",
                url
            )

    print(
        f"Working sources: {working}/{len(sources)}"
    )

    print("--------------------------------")


def update_jobs():

    print("================================")
    print("ROZGAR SATHI AUTOMATIC UPDATE")
    print("================================")

    today = today_date()

    print(
        "Today's date:",
        today
    )

    jobs = read_jobs(
        JOBS_FILE,
        "jobs"
    )

    closed_jobs = read_jobs(
        CLOSED_FILE,
        "closedJobs"
    )

    print(
        "Existing active jobs:",
        len(jobs)
    )

    print(
        "Existing closed jobs:",
        len(closed_jobs)
    )

    active_jobs, closed_jobs = remove_expired(
        jobs,
        closed_jobs
    )

    write_jobs(
        JOBS_FILE,
        "jobs",
        active_jobs
    )

    write_jobs(
        CLOSED_FILE,
        "closedJobs",
        closed_jobs
    )

    print("--------------------------------")
    print(
        "Active jobs:",
        len(active_jobs)
    )

    print(
        "Closed jobs:",
        len(closed_jobs)
    )

    print("--------------------------------")

    check_sources()

    print("Automatic update completed.")
    print("================================")


if __name__ == "__main__":
    update_jobs()
