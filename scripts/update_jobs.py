import os
import sys
import importlib
from datetime import datetime
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__)
    )
)

JOBS_FILE = "jobs-data.js"
CLOSED_FILE = "closed-jobs-data.js"


# =========================================================
# ROZGAR SATHI - AUTOMATIC JOB UPDATE ENGINE
# =========================================================

PARSERS = [

    ("SSC", "ssc_parser"),
    ("SBI", "sbi_parser"),
    ("RRB", "rrb_parser"),
    ("India Post", "india_post_parser"),
    ("IBPS", "ibps_parser"),
    ("UPSC", "upsc_parser"),

]


# =========================================================
# DATE
# =========================================================

def today():

    return datetime.now().date()


# =========================================================
# DATE PARSER
# =========================================================

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


# =========================================================
# READ OLD JOB DATABASE
# =========================================================

def read_existing_jobs():

    if not os.path.exists(
        JOBS_FILE
    ):

        return []


    with open(
        JOBS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        content = f.read()


    import re


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


    jobs = []


    for item in pattern.findall(
        content
    ):

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
# LOAD PARSER
# =========================================================

def load_parser(
    name,
    module_name
):

    try:

        module = importlib.import_module(
            module_name
        )

        if not hasattr(
            module,
            "get_jobs"
        ):

            print(
                f"[WARNING] {name}: get_jobs() नहीं मिला"
            )

            return []


        jobs = module.get_jobs()


        if not isinstance(
            jobs,
            list
        ):

            return []


        print(
            f"[OK] {name}: {len(jobs)} notices found"
        )


        return jobs


    except Exception as error:

        print(
            f"[ERROR] {name}: {error}"
        )

        return []


# =========================================================
# NORMALIZE JOB
# =========================================================

def normalize_job(job):

    return {

        "id":
        str(
            job.get(
                "id",
                ""
            )
        ).strip(),

        "title":
        str(
            job.get(
                "title",
                ""
            )
        ).strip(),

        "category":
        str(
            job.get(
                "category",
                "Government"
            )
        ).strip(),

        "qualification":
        str(
            job.get(
                "qualification",
                "Official notification के अनुसार"
            )
        ).strip(),

        "posts":
        str(
            job.get(
                "posts",
                "Official notification के अनुसार"
            )
        ).strip(),

        "lastDate":
        str(
            job.get(
                "lastDate",
                ""
            )
        ).strip(),

        "page":
        str(
            job.get(
                "page",
                ""
            )
        ).strip()

    }


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(
    jobs
):

    unique = {}


    for job in jobs:

        job = normalize_job(
            job
        )


        if not job["id"]:

            continue


        unique[
            job["id"]
        ] = job


    return list(
        unique.values()
    )


# =========================================================
# ACTIVE / CLOSED
# =========================================================

def split_jobs(
    jobs
):

    active = []

    closed = []

    current = today()


    for job in jobs:

        expiry = parse_date(
            job.get(
                "lastDate",
                ""
            )
        )


        # अगर last date available नहीं है
        # तो अभी job को active रखें।

        if expiry is None:

            active.append(
                job
            )

            continue


        if expiry < current:

            closed.append(
                job
            )

        else:

            active.append(
                job
            )


    return active, closed


# =========================================================
# JS SECURITY
# =========================================================

def escape_js(value):

    value = str(
        value or ""
    )


    return (

        value
        .replace(
            "\\",
            "\\\\"
        )
        .replace(
            '"',
            '\\"'
        )
        .replace(
            "\n",
            " "
        )
        .replace(
            "\r",
            " "
        )

    )


# =========================================================
# JOB → JAVASCRIPT
# =========================================================

def job_to_js(
    job
):

    return f'''{{
  id:"{escape_js(job["id"])}",
  title:"{escape_js(job["title"])}",
  category:"{escape_js(job["category"])}",
  qualification:"{escape_js(job["qualification"])}",
  posts:"{escape_js(job["posts"])}",
  lastDate:"{escape_js(job["lastDate"])}",
  page:"{escape_js(job["page"])}"
}}'''


# =========================================================
# WRITE DATABASE
# =========================================================

def write_database(
    filename,
    variable,
    jobs
):

    output = (

        f"const {variable} = [\n\n"

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

        f.write(
            output
        )


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

    print(
        "Date:",
        today()
    )


    # -----------------------------------------------------
    # OLD DATABASE
    # -----------------------------------------------------

    existing_jobs = (
        read_existing_jobs()
    )


    print(
        "Existing jobs:",
        len(existing_jobs)
    )


    # -----------------------------------------------------
    # PARSERS
    # -----------------------------------------------------

    collected_jobs = []


    for name, module_name in PARSERS:

        jobs = load_parser(
            name,
            module_name
        )


        collected_jobs.extend(
            jobs
        )


    print(
        "New notices:",
        len(collected_jobs)
    )


    # -----------------------------------------------------
    # COMBINE
    # -----------------------------------------------------

    all_jobs = (
        existing_jobs
        +
        collected_jobs
    )


    all_jobs = remove_duplicates(
        all_jobs
    )


    # -----------------------------------------------------
    # ACTIVE / CLOSED
    # -----------------------------------------------------

    active_jobs, closed_jobs = (
        split_jobs(
            all_jobs
        )
    )


    # -----------------------------------------------------
    # WRITE
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    print("")
    print(
        "Total:",
        len(all_jobs)
    )

    print(
        "Active:",
        len(active_jobs)
    )

    print(
        "Closed:",
        len(closed_jobs)
    )

    print("=" * 55)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    update_jobs()
