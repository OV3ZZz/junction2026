"""Complaint letter draft builder skeleton."""

from .schemas import Source


def build_draft(answer: str, sources: list[Source]) -> str:
    """Build a user-editable letter draft from the answer and its sources."""
    del answer, sources
    # TODO: Build a personalized complaint letter after the agent flow is implemented.
    return "Hei,\n\n[Lisää tähän vaatimuksesi ja tapahtuman tiedot.]\n\nYstävällisin terveisin,\n[Nimesi]"
