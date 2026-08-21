# Rozgar Sathi - Official Job Sources

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
        "url": "https://www.rrbcdg.gov.in/"
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


PRIVATE_SOURCES = {

    # Private section में केवल verified
    # company career sources जोड़े जाएंगे।

}


def get_government_sources():
    return GOVERNMENT_SOURCES


def get_private_sources():
    return PRIVATE_SOURCES
