import os
from pathlib import Path

from dotenv import load_dotenv

# Reads <repo>/.env if present. Real environment variables win over the file.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Send hours and "today" are in this timezone.
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./staff_email.db")

# Years of service that get a milestone email. 25 is handled as Silver Jubilee.
MILESTONE_YEARS = {5, 10, 15, 20, 30, 35, 40}
SILVER_JUBILEE_YEARS = 25

# Microsoft Graph. If any are empty the sender runs in mock mode (no real mail).
GRAPH_TENANT_ID = os.environ.get("GRAPH_TENANT_ID", "")
GRAPH_CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID", "")
GRAPH_CLIENT_SECRET = os.environ.get("GRAPH_CLIENT_SECRET", "")
GRAPH_SENDER_MAILBOX = os.environ.get("GRAPH_SENDER_MAILBOX", "")

# AI. Empty key means template-only drafts.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

# Occasions that always need a human, whatever the rule says.
ALWAYS_REVIEW = {"retirement", "promotion", "silver_jubilee"}
