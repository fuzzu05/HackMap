import hashlib
import re
from datetime import datetime, timezone
from typing import Tuple
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from ..models.hackathon import HackathonMode

# Simple baseline currency conversion rates to USD for normalization
CURRENCY_RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.28,
    "CAD": 0.73,
    "AUD": 0.65,
    "INR": 0.012,
}


def normalize_date_to_utc(date_str: str) -> str:
    """
    Parses arbitrary date strings into standard UTC ISO-8601 format (YYYY-MM-DDTHH:MM:SSZ).
    """
    if not date_str or not date_str.strip():
        raise ValueError("Cannot normalize empty date string")
    try:
        dt = date_parser.parse(date_str)
        if dt.tzinfo is None:
            # Assume UTC if tz info is missing
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        raise ValueError(f"Failed to parse date '{date_str}': {str(e)}")


def normalize_currency(amount: float, from_currency: str = "USD") -> float:
    """
    Normalizes prize pool amounts to USD based on standard currency conversion rates.
    """
    curr = from_currency.upper().strip()
    rate = CURRENCY_RATES_TO_USD.get(curr, 1.0)
    return round(amount * rate, 2)


def parse_prize_pool(prize_str: str) -> Tuple[float, str]:
    """
    Extracts numerical prize pool amount and currency code from a prize description string.
    Example: '$50,000 USD' -> (50000.0, 'USD')
    """
    if not prize_str:
        return 0.0, "USD"

    # Identify currency symbol or code
    currency = "USD"
    upper_str = prize_str.upper()
    for code in CURRENCY_RATES_TO_USD.keys():
        if code in upper_str:
            currency = code
            break
    if "€" in prize_str:
        currency = "EUR"
    elif "£" in prize_str:
        currency = "GBP"
    elif "₹" in prize_str:
        currency = "INR"

    # Extract digits and decimal point
    cleaned = re.sub(r"[^\d.]", "", prize_str.replace(",", ""))
    try:
        amount = float(cleaned) if cleaned else 0.0
    except ValueError:
        amount = 0.0

    return amount, currency


def normalize_tag(tag: str) -> str:
    """
    Cleans and standardizes tag names (e.g., '  ai / machine-learning ' -> 'AI / Machine Learning').
    """
    cleaned = re.sub(r"\s+", " ", tag.strip())
    # Title-case keywords while preserving AI, ML, API, LLM abbreviations
    upper_keywords = {"ai", "ml", "api", "llm", "llms", "ui", "ux", "vr", "ar", "nft", "web3", "aws", "gcp"}
    words = cleaned.split(" ")
    normalized_words = [
        w.upper() if w.lower() in upper_keywords else w.capitalize() for w in words
    ]
    return " ".join(normalized_words)


def normalize_mode(mode_str: str) -> HackathonMode:
    """
    Maps varied mode descriptions to standard HackathonMode enum values.
    """
    lower_val = mode_str.lower()
    if "hybrid" in lower_val:
        return HackathonMode.HYBRID
    elif any(k in lower_val for k in ("online", "remote", "virtual")):
        return HackathonMode.ONLINE
    elif any(k in lower_val for k in ("in-person", "in person", "onsite", "physical")):
        return HackathonMode.IN_PERSON
    return HackathonMode.ONLINE


def generate_dedup_hash(title: str, start_date: str) -> str:
    """
    Generates a deterministic similarity fingerprint hash for deduplicating cross-listed events.
    Uses alphanumeric normalized title token sequence + YYYY-MM start date prefix.
    """
    clean_title = re.sub(r"[^a-z0-9]", "", title.lower())
    # Use YYYY-MM prefix from ISO start date to group events occurring in same month
    date_prefix = start_date[:7] if len(start_date) >= 7 else "unknown"
    fingerprint = f"{clean_title}_{date_prefix}"
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:24]


def clean_html_text(html_content: str) -> str:
    """
    Strips raw HTML tags and scripts, returning clean readable text/markdown for description field.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()
    text = soup.get_text(separator="\n")
    # Clean excessive newlines and whitespace
    cleaned_lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in cleaned_lines if line).strip()
