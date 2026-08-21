import re
import urllib.request
from datetime import datetime

JOBS_FILE = "jobs-data.js"
CLOSED_FILE = "closed-jobs-data.js"

# =========================================================
# ROZGAR SATHI - AUTOMATIC JOB DATABASE
# =========================================================

try:
    from sources import (
        get_government_sources,
        get_private_sources
    )
except ImportError:
    get_government_sources = lambda: {}
    get_private_sources = lambda: {}


# =========================================================
# DATE
# =========================================================

def today():
    return datetime.now().date()


def parse_date(value):

    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d %B %Y",
        "%d %b %Y"
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


# =========================================================
# CLEAN / SECURITY
# =========================================================

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


# =========================================================
# JOB → JAVASCRIPT
# =========================================================

def job_to_js(job):

    return f'''{{
  id:"{escape_js(job.get("id", ""))}",
  title:"{escape_js(job.get("title", ""))}",
  category:"{escape_js(job.get("category", ""))}",
  qualification:"{escape_js(job.get("qualification", ""))}",
  posts:"{escape_js(job.get("posts", ""))}",
  lastDate:"{escape_js(job.get("lastDate", ""))}",
  page:"{escape_js(job.get("page", ""))}"
}}'''


# =========================================================
# READ EXISTING JOBS
# =========================================================

def read_existing_jobs():

    try:

        with open(
            JOBS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

    except FileNotFoundError:

        print(
            "jobs-data.js नहीं मिली।"
        )

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


# =========================================================
# DOWNLOAD SOURCE
# =========================================================

def fetch_page(url):

    try:

        request = urllib.request.Request(

            url,

            headers={

                "User-Agent":
                "Mozilla/5.0 RozgarSathiBot/1.0"

            }

        )


        with urllib.request.urlopen(

            request,

            timeout=25

        ) as response:

            return response.read().decode(

                "utf-8",

                errors="ignore"

            )


    except Exception as error:

        print(
            "Source error:",
            url
        )

        print(
            str(error)
        )

        return ""


# =========================================================
# SOURCE CHECK
# =========================================================

def check_sources():

    print("")
    print(
        "Checking Government Sources..."
    )


    government_sources = (
        get_government_sources()
    )


    for name, source in (
        government_sources.items()
    ):

        print(
            "Government:",
            name
        )


        page = fetch_page(
            source["url"]
        )


        if page:

            print(
                "  ✓ Source available"
            )

        else:

            print(
                "  ✗ Source unavailable"
            )


    print("")
    print(
        "Checking Private Sources..."
    )


    private_sources = (
        get_private_sources()
    )


    for name, source in (
        private_sources.items()
    ):

        print(
            "Private:",
            name
        )


        page = fetch_page(
            source["url"]
        )


        if page:

            print(
                "  ✓ Source available"
            )

        else:

            print(
                "  ✗ Source unavailable"
            )


# =========================================================
# ACTIVE / CLOSED
# =========================================================

def split_active_closed(jobs):

    active = []

    closed = []

    current_date = today()


    for job in jobs:

        expiry = parse_date(
            job.get(
                "lastDate",
                ""
            )
        )


        # Last date नहीं है तो
        # existing job को सुरक्षित रखें

        if expiry is None:

            active.append(job)

            continue


        if expiry < current_date:

            closed.append(job)

        else:

            active.append(job)


    return active, closed


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicate_jobs(jobs):

    unique = {}

    for job in jobs:

        job_id = clean(
            job.get(
                "id",
                ""
            )
        )


        if not job_id:

            continue


        unique[job_id] = job


    return list(
        unique.values()
    )


# =========================================================
# WRITE DATABASE
# =========================================================

def write_database(
    filename,
    variable,
    jobs
):

    output = (
        "const "
        +
        variable
        +
        " = [\n\n"
    )


    if jobs:

        output += ",\n\n".join(

            job_to_js(job)

            for job in jobs

        )


    output += (
        "\n\n];\n"
    )


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            output
        )


# =========================================================
# AUTOMATIC SOURCE FRAMEWORK
# =========================================================

def collect_new_jobs():

    """
    यहाँ केवल verified parser/API/RSS
    से मिलने वाली वास्तविक vacancies
    जोड़ी जाएंगी।

    बिना वास्तविक notification data के
    कोई fake vacancy generate नहीं होगी।
    """

    new_jobs = []

    # Government
    government_sources = (
        get_government_sources()
    )


    # Private
    private_sources = (
        get_private_sources()
    )


    print("")
    print(
        "Government sources configured:",
        len(government_sources)
    )


    print(
        "Private sources configured:",
        len(private_sources)
    )


    return new_jobs


# =========================================================
# MAIN UPDATE
# =========================================================

def update_jobs():

    print("")
    print("=" * 55)
    print(
        "ROZGAR SATHI AUTOMATIC JOB SYSTEM"
    )
    print("=" * 55)


    # -----------------------------------------------------
    # पुराने jobs-data.js को पढ़ें
    # -----------------------------------------------------

    existing_jobs = (
        read_existing_jobs()
    )


    print(
        "Existing jobs:",
        len(existing_jobs)
    )


    # -----------------------------------------------------
    # Sources check
    # -----------------------------------------------------

    check_sources()


    # -----------------------------------------------------
    # नई verified vacancies
    # -----------------------------------------------------

    new_jobs = (
        collect_new_jobs()
    )


    print(
        "New verified jobs:",
        len(new_jobs)
    )


    # -----------------------------------------------------
    # पुरानी + नई vacancies
    # -----------------------------------------------------

    all_jobs = (
        existing_jobs
        +
        new_jobs
    )


    # -----------------------------------------------------
    # Duplicate हटाएँ
    # -----------------------------------------------------

    all_jobs = (
        remove_duplicate_jobs(
            all_jobs
        )
    )


    # -----------------------------------------------------
    # Active / Closed
    # -----------------------------------------------------

    active_jobs, closed_jobs = (
        split_active_closed(
            all_jobs
        )
    )


    # -----------------------------------------------------
    # Active database
    # -----------------------------------------------------

    write_database(

        JOBS_FILE,

        "jobs",

        active_jobs

    )


    # -----------------------------------------------------
    # Closed database
    # -----------------------------------------------------

    write_database(

        CLOSED_FILE,

        "closedJobs",

        closed_jobs

    )


    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    print("")
    print(
        "Today's date:",
        today()
    )


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


    print("=" * 55)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    update_jobs()
