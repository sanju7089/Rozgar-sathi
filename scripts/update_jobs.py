import re
import hashlib
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html import unescape


JOBS_FILE = "jobs-data.js"
CLOSED_FILE = "closed-jobs-data.js"

DRDO_URL = "https://drdo.gov.in/drdo/en/offerings/vacancies"
INDIA_POST_URL = "https://www.indiapost.gov.in/vacancies"
SBI_URL = "https://sbi.co.in/web/careers/current-openings"


# =========================================================
# DATE
# =========================================================

def today():
    return datetime.now().date()


def parse_date(value):

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return None


def convert_date(value):

    value = value.strip()

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d-%m-%y",
        "%d/%m/%y",
        "%d.%m.%y"
    ]

    for fmt in formats:

        try:

            return datetime.strptime(
                value,
                fmt
            ).strftime("%Y-%m-%d")

        except ValueError:
            pass

    return ""


# =========================================================
# HTML
# =========================================================

def clean_html(text):

    text = re.sub(
        r"<script.*?</script>",
        " ",
        text,
        flags=re.I | re.S
    )

    text = re.sub(
        r"<style.*?</style>",
        " ",
        text,
        flags=re.I | re.S
    )

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


def download(url):

    try:

        request = Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/120 Safari/537.36"
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
# JOB ID
# =========================================================

def make_id(prefix, title, date, page):

    raw = (
        prefix
        + "|"
        + title
        + "|"
        + date
        + "|"
        + page
    )

    return (
        prefix
        + "-"
        + hashlib.sha1(
            raw.encode("utf-8")
        ).hexdigest()[:12]
    )


# =========================================================
# JS
# =========================================================

def job_to_js(job):

    def clean(value):

        return (
            str(value)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", " ")
            .replace("\r", " ")
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
# READ DATABASE
# =========================================================

def read_jobs(filename):

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

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
# WRITE DATABASE
# =========================================================

def write_jobs(
    filename,
    variable,
    jobs
):

    output = (
        f"const {variable} = [\n\n"
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
    ) as file:

        file.write(output)


# =========================================================
# ADD JOBS + DUPLICATE PROTECTION
# =========================================================

def add_jobs(
    existing,
    new_jobs
):

    result = list(existing)

    ids = {
        job[0]
        for job in result
    }

    added = 0

    for job in new_jobs:

        if job[0] not in ids:

            result.append(job)

            ids.add(
                job[0]
            )

            added += 1

    return result, added


# =========================================================
# EXPIRED JOB SYSTEM
# =========================================================

def move_expired(
    active,
    closed
):

    active_result = []

    closed_result = list(
        closed
    )

    closed_ids = {
        job[0]
        for job in closed_result
    }

    moved = 0

    for job in active:

        expiry = parse_date(
            job[5]
        )

        if expiry is None:

            active_result.append(
                job
            )

            continue

        if expiry < today():

            if job[0] not in closed_ids:

                closed_result.append(
                    job
                )

                closed_ids.add(
                    job[0]
                )

                moved += 1

        else:

            active_result.append(
                job
            )

    return (
        active_result,
        closed_result,
        moved
    )


# =========================================================
# DRDO
# =========================================================

def scrape_drdo():

    print("--------------------------------")
    print("DRDO AUTOMATIC SCANNER")
    print("--------------------------------")

    jobs = []

    # DRDO current page + next pages
    for page_number in range(0, 3):

        if page_number == 0:

            url = DRDO_URL

        else:

            url = (
                DRDO_URL
                + "?page="
                + str(page_number)
            )

        html = download(url)

        if not html:
            continue

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

            if len(title) < 15:
                continue

            lower = title.lower()

            # Result/selection notices को vacancy नहीं मानना
            blocked = [
                "result",
                "selected candidate",
                "provisionally selected",
                "waitlisted",
                "corrigendum",
                "shortlisted",
                "answer key"
            ]

            if any(
                word in lower
                for word in blocked
            ):
                continue

            vacancy_words = [
                "application",
                "recruitment",
                "apprentice",
                "jrf",
                "research associate",
                "scientist",
                "technician",
                "project assistant",
                "internship"
            ]

            if not any(
                word in lower
                for word in vacancy_words
            ):
                continue

            page_url = urljoin(
                url,
                href
            )

            position = html.find(
                raw_title
            )

            if position < 0:
                continue

            nearby = html[
                position:
                position + 6000
            ]

            text = clean_html(
                nearby
            )

            dates = re.findall(
                r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
                text
            )

            if not dates:
                continue

            last_date = ""

            for date_value in dates:

                converted = convert_date(
                    date_value
                )

                if converted:

                    last_date = converted

            if not last_date:
                continue

            expiry = parse_date(
                last_date
            )

            if expiry is None:
                continue

            if expiry < today():
                continue

            job_id = make_id(
                "drdo",
                title,
                last_date,
                page_url
            )

            jobs.append((
                job_id,
                title,
                "Government • Defence • DRDO",
                "Notification के अनुसार",
                "Multiple / Notification के अनुसार",
                last_date,
                page_url
            ))

    unique = {}

    for job in jobs:

        unique[job[0]] = job

    jobs = list(
        unique.values()
    )

    print(
        "DRDO vacancies found:",
        len(jobs)
    )

    return jobs


# =========================================================
# INDIA POST
# =========================================================

def scrape_india_post():

    print("--------------------------------")
    print("INDIA POST AUTOMATIC SCANNER")
    print("--------------------------------")

    html = download(
        INDIA_POST_URL
    )

    if not html:
        return []

    jobs = []

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

        if len(title) < 20:
            continue

        lower = title.lower()

        allowed = [
            "recruitment",
            "vacancies",
            "vacancy",
            "driver",
            "skilled artisan",
            "staff car",
            "postman",
            "assistant"
        ]

        if not any(
            word in lower
            for word in allowed
        ):
            continue

        blocked = [
            "corrigendum",
            "result",
            "merit list",
            "selected candidate",
            "shortlisted",
            "answer key"
        ]

        if any(
            word in lower
            for word in blocked
        ):
            continue

        page_url = urljoin(
            INDIA_POST_URL,
            href
        )

        # India Post listing पर कई बार last date
        # नहीं होती; detail/PDF के आसपास खोजें
        position = html.find(
            raw_title
        )

        nearby = html[
            position:
            position + 7000
        ]

        text = clean_html(
            nearby
        )

        dates = re.findall(
            r'\b\d{2}[-/.]\d{2}[-/.]\d{4}\b',
            text
        )

        if not dates:
            continue

        last_date = ""

        for value in dates:

            converted = convert_date(
                value
            )

            if converted:
                last_date = converted

        if not last_date:
            continue

        expiry = parse_date(
            last_date
        )

        if expiry is None:
            continue

        if expiry < today():
            continue

        job_id = make_id(
            "indiapost",
            title,
            last_date,
            page_url
        )

        jobs.append((
            job_id,
            title,
            "Government • India Post",
            "Notification के अनुसार",
            "Notification के अनुसार",
            last_date,
            page_url
        ))

    unique = {}

    for job in jobs:

        unique[job[0]] = job

    jobs = list(
        unique.values()
    )

    print(
        "India Post vacancies found:",
        len(jobs)
    )

    return jobs


# =========================================================
# SBI
# =========================================================

def scrape_sbi():

    print("--------------------------------")
    print("SBI AUTOMATIC SCANNER")
    print("--------------------------------")

    html = download(
        SBI_URL
    )

    if not html:
        return []

    jobs = []

    # SBI page पर Last Date to Apply के आसपास
    # recruitment title ढूँढना
    date_pattern = re.compile(
        r'LAST\s+DATE\s+TO\s+APPLY\s*:?\s*'
        r'(\d{2}[-/.]\d{2}[-/.]\d{4})',
        re.I
    )

    matches = list(
        date_pattern.finditer(html)
    )

    for match in matches:

        date_value = match.group(1)

        last_date = convert_date(
            date_value
        )

        if not last_date:
            continue

        expiry = parse_date(
            last_date
        )

        if expiry is None:
            continue

        if expiry < today():
            continue

        # Last date से पहले का HTML block
        start = max(
            0,
            match.start() - 5000
        )

        before_html = html[
            start:
            match.start()
        ]

        text = clean_html(
            before_html
        )

        # Candidate title lines
        candidates = re.split(
            r'(?<=[.!?])\s+|(?=\b(?:RECRUITMENT|ENGAGEMENT)\b)',
            text
        )

        title = ""

        # पहले uppercase recruitment title ढूँढें
        for candidate in reversed(
            candidates
        ):

            candidate = candidate.strip()

            upper = candidate.upper()

            if (
                "RECRUITMENT" in upper
                or
                "ENGAGEMENT" in upper
            ):

                if len(candidate) >= 25:

                    title = candidate

                    break

        # दूसरा fallback
        if not title:

            found = re.findall(
                r'(?:RECRUITMENT|ENGAGEMENT)[^.!?]{20,350}',
                text,
                flags=re.I
            )

            if found:

                title = found[-1].strip()

        if not title:
            continue

        # अनावश्यक text साफ करें
        title = re.sub(
            r'\s+',
            ' ',
            title
        ).strip()

        # HTML/UI text से बचाव
        blocked = [
            "result",
            "selected",
            "interview schedule",
            "call letter",
            "provisionally selected",
            "answer key",
            "shortlisted"
        ]

        lower = title.lower()

        if any(
            word in lower
            for word in blocked
        ):
            continue

        # Title बहुत बड़ा हो तो छोटा करें
        if len(title) > 350:

            title = title[:350].strip()

        page_url = SBI_URL

        job_id = make_id(
            "sbi",
            title,
            last_date,
            page_url
        )

        jobs.append((
            job_id,
            title,
            "Bank • SBI • All India",
            "Notification के अनुसार",
            "Notification के अनुसार",
            last_date,
            page_url
        ))

    unique = {}

    for job in jobs:

        unique[job[0]] = job

    jobs = list(
        unique.values()
    )

    print(
        "SBI vacancies found:",
        len(jobs)
    )

    return jobs


# =========================================================
# MAIN UPDATE
# =========================================================

def update():

    print("================================")
    print("ROZGAR SATHI AUTO JOB SYSTEM")
    print("================================")

    print(
        "Today's date:",
        today()
    )

    # Existing database
    active = read_jobs(
        JOBS_FILE
    )

    closed = read_jobs(
        CLOSED_FILE
    )

    print(
        "Existing active jobs:",
        len(active)
    )

    print(
        "Existing closed jobs:",
        len(closed)
    )


    # -----------------------------------------------------
    # STEP 1
    # Expired jobs -> Closed
    # -----------------------------------------------------

    (
        active,
        closed,
        moved
    ) = move_expired(
        active,
        closed
    )

    print(
        "Expired jobs moved:",
        moved
    )


    # -----------------------------------------------------
    # STEP 2
    # DRDO
    # -----------------------------------------------------

    drdo_jobs = scrape_drdo()

    (
        active,
        drdo_added
    ) = add_jobs(
        active,
        drdo_jobs
    )

    print(
        "New DRDO jobs added:",
        drdo_added
    )


    # -----------------------------------------------------
    # STEP 3
    # INDIA POST
    # -----------------------------------------------------

    india_post_jobs = scrape_india_post()

    (
        active,
        post_added
    ) = add_jobs(
        active,
        india_post_jobs
    )

    print(
        "New India Post jobs added:",
        post_added
    )


    # -----------------------------------------------------
    # STEP 4
    # SBI
    # -----------------------------------------------------

    sbi_jobs = scrape_sbi()

    (
        active,
        sbi_added
    ) = add_jobs(
        active,
        sbi_jobs
    )

    print(
        "New SBI jobs added:",
        sbi_added
    )


    # -----------------------------------------------------
    # STEP 5
    # FINAL DATABASE SAVE
    # -----------------------------------------------------

    write_jobs(
        JOBS_FILE,
        "jobs",
        active
    )

    write_jobs(
        CLOSED_FILE,
        "closedJobs",
        closed
    )


    # -----------------------------------------------------
    # FINAL REPORT
    # -----------------------------------------------------

    print("--------------------------------")

    print(
        "Final active jobs:",
        len(active)
    )

    print(
        "Final closed jobs:",
        len(closed)
    )

    print(
        "DRDO added:",
        drdo_added
    )

    print(
        "India Post added:",
        post_added
    )

    print(
        "SBI added:",
        sbi_added
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

    update()
