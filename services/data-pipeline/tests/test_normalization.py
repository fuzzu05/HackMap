import pytest
from src.normalization.normalizer import (
    normalize_date_to_utc,
    normalize_currency,
    parse_prize_pool,
    normalize_tag,
    normalize_mode,
    generate_dedup_hash,
    clean_html_text,
)
from src.models.hackathon import HackathonMode


def test_normalize_date_to_utc():
    iso_date = normalize_date_to_utc("2026-09-05T10:00:00")
    assert iso_date == "2026-09-05T10:00:00Z"


def test_normalize_currency():
    usd = normalize_currency(100.0, "EUR")
    assert usd == 108.0


def test_parse_prize_pool():
    amount, curr = parse_prize_pool("$50,000 USD")
    assert amount == 50000.0
    assert curr == "USD"

    amount_eur, curr_eur = parse_prize_pool("€10,000")
    assert amount_eur == 10000.0
    assert curr_eur == "EUR"


def test_normalize_tag():
    res = normalize_tag("  ai / machine-learning ")
    assert "AI" in res


def test_normalize_mode():
    assert normalize_mode("hybrid event") == HackathonMode.HYBRID
    assert normalize_mode("In-person hackathon") == HackathonMode.IN_PERSON
    assert normalize_mode("Online virtual") == HackathonMode.ONLINE


def test_generate_dedup_hash():
    h1 = generate_dedup_hash("Global AI Hackathon 2026", "2026-09-05T00:00:00Z")
    h2 = generate_dedup_hash("Global AI Hackathon 2026", "2026-09-05T00:00:00Z")
    assert h1 == h2
    assert len(h1) == 24


def test_clean_html_text():
    html = "<div><script>alert(1);</script><p>Welcome to <b>HackMap</b>!</p></div>"
    clean = clean_html_text(html)
    assert "alert" not in clean
    assert "Welcome to HackMap!" in clean
