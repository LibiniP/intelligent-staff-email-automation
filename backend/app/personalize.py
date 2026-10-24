"""Context building, drafting, and the fact guard.

Facts come only from the DB. The LLM may reword, but the guard rejects any
draft that adds numbers, or drops the name, so nothing invented gets through.
"""
import re
from string import Template as StrTemplate

from . import config
from .milestones import Occasion, service_duration_text

SUBJECT_FALLBACK = {
    "birthday": "Happy Birthday, $name!",
    "joining_anniversary": "Celebrating your journey with Amrita, $name",
    "service_milestone": "Congratulations on $years years of service, $name",
    "silver_jubilee": "Silver Jubilee: 25 years with Amrita, $name",
    "retirement": "With gratitude, $name",
}


def build_context(staff, occ: Occasion) -> dict:
    """Verified facts only. Anything not here cannot appear in an email."""
    ctx = {
        "name": staff.preferred_name or staff.name,
        "department": staff.department,
        "designation": staff.designation,
    }
    if occ.years is not None:
        ctx["years"] = str(occ.years)
        ctx["duration"] = service_duration_text(staff.joining_date, occ.on)
    return ctx


def render(template, ctx: dict) -> tuple[str, str]:
    subject = StrTemplate(template.subject).safe_substitute(ctx)
    body = StrTemplate(template.body).safe_substitute(ctx)
    return subject, body


def guard(text: str, ctx: dict) -> list[str]:
    """Return a list of problems. Empty list means the draft is allowed."""
    problems = []
    if ctx["name"] not in text:
        problems.append("recipient name missing")
    if re.search(r"\$\{?\w+\}?", text):
        problems.append("unfilled placeholder")
    allowed = {n for v in ctx.values() for n in re.findall(r"\d+", v)}
    for num in re.findall(r"\d+", text):
        if num not in allowed:
            problems.append(f"unverified number: {num}")
    return problems


def _llm_polish(subject: str, body: str, ctx: dict, occasion: str) -> str | None:
    """Ask Claude to smooth the wording. Returns new body, or None on any failure."""
    if not config.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=600,
            system=(
                "You polish a staff email for a university. Use ONLY the facts "
                "given. Do not add dates, numbers, achievements or duties. Keep "
                "the recipient's name. Return the email body only."
            ),
            messages=[{"role": "user", "content": f"Occasion: {occasion}\nFacts: {ctx}\nDraft:\n{body}"}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return None


def draft_email(template, staff, occ: Occasion) -> tuple[str, str, str]:
    """Return (subject, body, generated_by). Falls back to the template on guard failure."""
    ctx = build_context(staff, occ)
    subject, body = render(template, ctx)
    polished = _llm_polish(subject, body, ctx, occ.kind)
    if polished and not guard(polished, ctx):
        return subject, polished, "llm"
    return subject, body, "template"
