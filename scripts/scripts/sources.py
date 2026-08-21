# =========================================================
# ROZGAR SATHI - OFFICIAL JOB SOURCES
# =========================================================

GOVERNMENT_SOURCES = {

    "SSC": {
        "category": "Government",
        "url": "https://ssc.gov.in/"
    },

    "UPSC": {
        "category": "Government",
        "url": "https://www.upsc.gov.in/recruitment/recruitment-advertisement"
    },

    "RRB": {
        "category": "Government",
        "url": "https://www.rrbbhopal.gov.in/"
    },

    "India Post": {
        "category": "Government",
        "url": "https://indiapostgdsonline.gov.in/"
    },

    "IBPS": {
        "category": "Banking",
        "url": "https://www.ibps.in/"
    },

    "SBI": {
        "category": "Banking",
        "url": "https://sbi.bank.in/web/careers"
    }

}


# =========================================================
# PRIVATE COMPANY SOURCES
# =========================================================

PRIVATE_SOURCES = {

    # Private companies बाद में यहाँ
    # केवल official career pages से जोड़ी जाएँगी।

}


# =========================================================
# SOURCE FUNCTIONS
# =========================================================

def get_government_sources():

    return GOVERNMENT_SOURCES


def get_private_sources():

    return PRIVATE_SOURCES


# =========================================================
# SOURCE CATEGORY
# =========================================================

def get_source_category(source_name):

    if source_name in GOVERNMENT_SOURCES:

        return GOVERNMENT_SOURCES[
            source_name
        ]["category"]


    if source_name in PRIVATE_SOURCES:

        return PRIVATE_SOURCES[
            source_name
        ]["category"]


    return "Other"


# =========================================================
# SOURCE URL
# =========================================================

def get_source_url(source_name):

    if source_name in GOVERNMENT_SOURCES:

        return GOVERNMENT_SOURCES[
            source_name
        ]["url"]


    if source_name in PRIVATE_SOURCES:

        return PRIVATE_SOURCES[
            source_name
        ]["url"]


    return ""
