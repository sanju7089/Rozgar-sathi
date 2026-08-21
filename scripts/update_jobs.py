import re
from datetime import datetime

JOBS_FILE = "jobs-data.js"
CLOSED_FILE = "closed-jobs-data.js"


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


def update_jobs():

    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    today = datetime.now().date()

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

    jobs = pattern.findall(content)

    active_jobs = []
    closed_jobs = []

    for job in jobs:

        try:
            expiry_date = parse_date(job[5])
        except ValueError:
            active_jobs.append(job)
            continue

        if expiry_date < today:
            closed_jobs.append(job)
        else:
            active_jobs.append(job)

    # Active jobs update
    active_js = "const jobs = [\n\n"

    active_js += ",\n\n".join(
        job_to_js(job) for job in active_jobs
    )

    active_js += "\n\n];\n"

    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        f.write(active_js)

    # Closed jobs update
    closed_js = "const closedJobs = [\n\n"

    closed_js += ",\n\n".join(
        job_to_js(job) for job in closed_jobs
    )

    closed_js += "\n\n];\n"

    with open(CLOSED_FILE, "w", encoding="utf-8") as f:
        f.write(closed_js)

    print("================================")
    print("ROZGAR SATHI AUTOMATIC UPDATE")
    print("================================")
    print(f"Today's date: {today}")
    print(f"Total jobs: {len(jobs)}")
    print(f"Active jobs: {len(active_jobs)}")
    print(f"Closed jobs: {len(closed_jobs)}")
    print("================================")


if __name__ == "__main__":
    update_jobs()
