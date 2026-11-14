"""Duplicate detection across sites and deadline parsing."""

from datetime import date

from app import deadline
from app.dedupe import same_job


def test_same_title_same_employer_is_duplicate() -> None:
    assert same_job("Asiakaspalvelija", "Firma Oy", "Asiakaspalvelija | Duunitori", "Firma")


def test_employer_in_other_title_is_duplicate() -> None:
    assert same_job("Hankinta-assistentti", "HankintaPartners Oy",
                    "Hankinta-assistentti, HankintaPartners Oy", "Eilakaisla Oy")


def test_same_title_other_employer_is_not_duplicate() -> None:
    assert not same_job("Asiakaspalvelija", "Firma Oy", "Asiakaspalvelija", "Toinen Ab")


def test_missing_employer_needs_identical_title() -> None:
    assert same_job("Tarjoilija", None, "Tarjoilija", "Ravintola Oy")
    assert not same_job("Tarjoilija", None, "Tarjoilija, osa-aikainen", None)


def test_deadline_formats() -> None:
    assert deadline.parse("2026-11-19") == date(2026, 11, 19)
    assert deadline.parse("Haku päättyy Asti 2.8.2026 (ilmoituksessa ...)") == date(2026, 8, 2)
    assert deadline.parse("Haetaan heti") is None


def test_expired_and_display() -> None:
    today = date(2026, 11, 14)
    assert deadline.is_expired("2.8.2026", today)
    assert not deadline.is_expired("2026-11-14", today)
    assert not deadline.is_expired("toistaiseksi", today)
    assert deadline.display("2026-12-01") == "1.12.2026"
    assert deadline.display("Haetaan heti") == "Haetaan heti"
    assert deadline.display("x" * 40) is None
