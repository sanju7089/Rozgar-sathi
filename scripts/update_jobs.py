import re
import json
import hashlib
from datetime import datetime
from urllib.request import Request, urlopen
from html import unescape


JOBS_FILE = "jobs-data.js"
CLOSED_FILE = "closed-jobs-data.js"
SOURCES_FILE = "job-sources.json"

DRDO_URL = "https://drdo.gov.in/drdo/en/offerings/vacancies"


# =========================================================
# BASIC FUNCTIONS
# =========================================================

def today_date():
    return datetime.now().date()


def parse_date(date_string):
    return datetime.strptime(
        date_string,
        "%Y-%m-%d"
    ).date()


def job_to_js(job):

    def clean(value):
        return str(value).replace(
            "\\",
            "\\\\"
        ).replace(
            '"',
            '\\"'
        )

    return f'''{{
  id:"{clean(job[0])}",
  title:"{clean(job[1])}",
  category:"{clean(job[2])}",
  qualification:"{clean(job[3])}",
  posts:"{clean(job[4])}",
  lastDate:"{clean(job[5])}",
  page:"{clean(job[6])}"
}}'''


# =========================================================
# READ EXISTING JOB DATABASE
# =========================================================

def read_jobs(filename):

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

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


# =========================================================
# WRITE JOB DATABASE
# =========================================================

def write_jobs(
    filename,
    variable_name,
    jobs
):

    output = (
        f"const {variable_name} = [\n\n"
    )


    if jobs:

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


# =========================================================
# DOWNLOAD WEB PAGE
# =========================================================

def download_page(url):

    try:

        request = Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0 "
                "(Rozgar-Sathi-Automatic-Bot)"
            }
        )


        with urlopen(
            request,
            timeout=30
        ) as response:

            return response.read().decode(
                "utf-8",
                errors="ignore"
            )


    except Exception as error:

        print(
            "Download failed:",
            url,
            error
        )

        return ""


# =========================================================
# HTML CLEANING
# =========================================================

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


# =========================================================
# DATE CONVERSION
# =========================================================

def convert_date(date_string):

    date_string = date_string.strip()


    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d/%m/%y",
        "%d-%m-%y"
    ]


    for fmt in formats:

        try:

            return datetime.strptime(
                date_string,
                fmt
            ).strftime("%Y-%m-%d")

        except ValueError:

            pass


    return ""


# =========================================================
# DRDO TITLE FILTER
# =========================================================

def is_real_drdo_vacancy(title):

    title_lower = title.lower()


    blocked_words = [

        "result",

        "selected candidate",

        "provisionally selected",

        "waitlisted",

        "selection list",

        "corrigendum",

        "shortlisted",

        "admit card",

        "answer key",

        "skill-seeker"

    ]


    for word in blocked_words:

        if word in title_lower:

            return False


    vacancy_words = [

        "invite",

        "invites",

        "application",

        "applications",

        "recruitment",

        "apprentice",

        "fellowship",

        "jrf",

        "research associate",

        "ra & jrf",

        "project assistant",

        "scientist",

        "technician",

        "internship"

    ]


    return any(
        word in title_lower
        for word in vacancy_words
    )


# =========================================================
# DRDO SCRAPER
# =========================================================

def scrape_drdo():

    print("--------------------------------")
    print("DRDO AUTOMATIC VACANCY SCANNER")
    print("--------------------------------")


    new_jobs = []


    # Current page + next pages
    for page_number in range(0, 3):

        if page_number == 0:

            url = DRDO_URL

        else:

            url = (
                DRDO_URL
                +
                "?page="
                +
                str(page_number)
            )


        print(
            "Scanning:",
            url
        )


        html = download_page(url)


        if not html:

            continue


        # -------------------------------------------------
        # Find vacancy links
        # -------------------------------------------------

        links = re.findall(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
            r'(.*?)'
            r'</a>',
            html,
            flags=re.I | re.S
        )


        for href, raw_title in links:

            title = clean_html(
                raw_title
            )


            if not title:

                continue


            if len(title) < 15:

                continue


            if not is_real_drdo_vacancy(
                title
            ):

                continue


            # Only links which look like
            # DRDO vacancy detail pages
            if (
                "vacanc" not in href.lower()
                and
                "career" not in href.lower()
                and
                "recruit" not in href.lower()
            ):

                continue


            if href.startswith("/"):

                page_url = (
                    "https://drdo.gov.in"
                    +
                    href
                )

            elif href.startswith("http"):

                page_url = href

            else:

                continue


            # -------------------------------------------------
            # Find nearby dates
            # -------------------------------------------------

            link_position = html.find(
                raw_title
            )


            if link_position < 0:

                continue


            nearby_html = html[
                link_position:
                link_position + 5000
            ]


            nearby_text = clean_html(
                nearby_html
            )


            date_matches = re.findall(
                r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
                nearby_text
            )


            if not date_matches:

                continue


            last_date = ""


            # Usually the last displayed date
            # in the vacancy block is End Date.
            for date_value in date_matches:

                converted = convert_date(
                    date_value
                )

                if converted:

                    last_date = converted


            if not last_date:

                continue


            # -------------------------------------------------
            # Don't add already expired vacancy
            # -------------------------------------------------

            try:

                if parse_date(
                    last_date
                ) < today_date():

                    continue

            except ValueError:

                continue


            # -------------------------------------------------
            # Unique ID
            # -------------------------------------------------

            unique_text = (
                title
                +
                "|"
                +
                last_date
                +
                "|"
                +
                page_url
            )


            job_id = (
                "drdo-"
                +
                hashlib.sha1(
                    unique_text.encode(
                        "utf-8"
                    )
                ).hexdigest()[:12]
            )


            job = (

                job_id,

                title,

                "Government • Defence • DRDO",

                "Notification के अनुसार",

                "Multiple / Notification के अनुसार",

                last_date,

                page_url

            )


            # Duplicate protection

            if not any(
                existing[0] == job_id
                for existing in new_jobs
            ):

                new_jobs.append(job)


    print(
        "DRDO vacancies found:",
        len(new_jobs)
    )


    return new_jobs


# =========================================================
# ADD NEW JOBS
# =========================================================

def merge_new_jobs(
    existing_jobs,
    scraped_jobs
):

    result = list(
        existing_jobs
    )


    existing_ids = {
        job[0]
        for job in existing_jobs
    }


    added = 0


    for job in scraped_jobs:

        if job[0] not in existing_ids:

            result.append(job)

            existing_ids.add(
                job[0]
            )

            added += 1


    return result, added


# =========================================================
# MOVE EXPIRED JOBS
# =========================================================

def move_expired_jobs(
    jobs,
    closed_jobs
):

    today = today_date()


    active_jobs = []

    closed = list(
        closed_jobs
    )


    closed_ids = {
        job[0]
        for job in closed
    }


    moved = 0


    for job in jobs:

        try:

            expiry_date = parse_date(
                job[5]
            )

        except ValueError:

            active_jobs.append(job)

            continue


        if expiry_date < today:

            if job[0] not in closed_ids:

                closed.append(job)

                closed_ids.add(
                    job[0]
                )

                moved += 1

        else:

            active_jobs.append(job)


    return (
        active_jobs,
        closed,
        moved
    )


# =========================================================
# MAIN UPDATE
# =========================================================

def update_jobs():

    print("================================")
    print("ROZGAR SATHI AUTOMATIC SYSTEM")
    print("================================")

    print(
        "Today's date:",
        today_date()
    )


    # Existing databases

    active_jobs = read_jobs(
        JOBS_FILE
    )

    closed_jobs = read_jobs(
        CLOSED_FILE
    )


    print(
        "Existing active jobs:",
        len(active_jobs)
    )


    print(
        "Existing closed jobs:",
        len(closed_jobs)
    )


    # -----------------------------------------------------
    # 1. Remove expired jobs first
    # -----------------------------------------------------

    (
        active_jobs,
        closed_jobs,
        moved_count
    ) = move_expired_jobs(
        active_jobs,
        closed_jobs
    )


    print(
        "Moved to closed:",
        moved_count
    )


    # -----------------------------------------------------
    # 2. Scan DRDO
    # -----------------------------------------------------

    drdo_jobs = scrape_drdo()


    # -----------------------------------------------------
    # 3. Add new DRDO jobs
    # -----------------------------------------------------

    (
        active_jobs,
        added_count
    ) = merge_new_jobs(
        active_jobs,
        drdo_jobs
    )


    print(
        "New DRDO jobs added:",
        added_count
    )


    # -----------------------------------------------------
    # 4. Save databases
    # -----------------------------------------------------

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
        "Final active jobs:",
        len(active_jobs)
    )

    print(
        "Final closed jobs:",
        len(closed_jobs)
    )

    print("--------------------------------")

    print(
        "ROZGAR SATHI UPDATE COMPLETE"
    )

    print("================================")


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    update_jobs()
