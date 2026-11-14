"""Complaint letter draft builder."""

from .config import get_gemini_key
from .llm import chat
from .schemas import Source

TEMPLATE = (
    "Hei,\n\n[Lisää tähän vaatimuksesi ja tapahtuman tiedot.]\n\n"
    "Ystävällisin terveisin,\n[Nimesi]"
)

DRAFT_PROMPT = """Write a short, polite but firm complaint letter that the consumer can send \
to the company. Use the same language as the consumer's description. Base the demands only on \
the research summary. Use placeholders in square brackets for anything unknown, such as \
[Nimesi], [Varausnumero] or [Päivämäärä]. Return only the letter text."""


def build_draft(description: str, answer: str, sources: list[Source]) -> str:
    """Build a user-editable letter draft from the claim, the answer and its sources."""
    if not get_gemini_key():
        return TEMPLATE
    source_list = "\n".join(f"- {source.title}: {source.url}" for source in sources)
    content = (
        f"Consumer's description:\n{description}\n\n"
        f"Research summary:\n{answer}\n\nSources:\n{source_list}"
    )
    message = chat([
        {"role": "system", "content": DRAFT_PROMPT},
        {"role": "user", "content": content},
    ])
    return message.content or TEMPLATE
