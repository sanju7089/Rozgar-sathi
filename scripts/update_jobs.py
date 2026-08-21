import re
from datetime import datetime

JOBS_FILE = "jobs-data.js"


def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()


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

        job_id = job[0]
        title = job[1]
        category = job[2]
        qualification = job[3]
        posts = job[4]
        last_date = job[5]
        page = job[6]

        try:
            expiry_date = parse_date(last_date)
        except ValueError:
            print(f"Invalid date: {last_date}")
            active_jobs.append(job)
            continue

        if expiry_date < today:
            closed_jobs.append(job)
        else:
            active_jobs.append(job)

    print("================================")
    print("ROZGAR SATHI JOB UPDATE")
    print("================================")

    print(f"Today's date: {today}")
    print(f"Total jobs: {len(jobs)}")
    print(f"Active jobs: {len(active_jobs)}")
    print(f"Expired jobs: {len(closed_jobs)}")

    if closed_jobs:

        print("\nExpired Jobs:")

        for job in closed_jobs:
            print("-", job[1], "|", job[5])

    print("\nActive Jobs:")

    for job in active_jobs:
        print("-", job[1], "|", job[5])

    print("\nUpdate check completed.")


if __name__ == "__main__":
    update_jobs()
