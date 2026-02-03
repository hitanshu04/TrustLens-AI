import re
from typing import List, Tuple

from app.core.config import settings


URL_REGEX = re.compile(
    r"(https?://[^\s]+)",
    flags=re.IGNORECASE,
)


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from the given text using a simple regex.
    """

    return URL_REGEX.findall(text or "")


def check_url_reputation(text: str) -> Tuple[float, List[str], List[str]]:
    """
    Inspect URLs in the text and return:

    - score: a contribution between 0 and 1 representing URL-related risk
    - suspicious_urls: URLs that look suspicious (e.g. shortened links)
    - reasons: human-readable explanations for the score
    """

    urls = extract_urls(text)
    if not urls:
        return 0.0, [], []

    suspicious_urls: List[str] = []
    reasons: List[str] = []

    for url in urls:
        for short_domain in settings.SUSPICIOUS_SHORT_DOMAINS:
            domain_pattern = f"://{short_domain}/"
            if domain_pattern.lower() in url.lower():
                suspicious_urls.append(url)
                reasons.append(
                    f"Detected shortened URL using domain '{short_domain}', which is commonly "
                    "used to obscure final destinations in scam messages."
                )
                break

    # Basic heuristic: presence of any suspicious shortened URL is high risk.
    if suspicious_urls:
        score = 0.6
    else:
        # Non-shortened URLs are not necessarily safe but contribute a small baseline risk.
        score = 0.1
        reasons.append(
            "Message contains URLs; while none use known shortening services, links can still "
            "be used in phishing or scam campaigns."
        )

    return score, suspicious_urls, reasons
