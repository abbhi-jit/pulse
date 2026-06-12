import os
from pathlib import Path

import requests
from google import genai
from google.genai import types


WEATHER_URL = "https://wttr.in/Thiruvananthapuram?format=3"
OUTPUT_FILE = Path("daily_summary.txt")
FALLBACK_BRIEFING = "AI Briefing unavailable today."


def fetch_weather_summary() -> str:
    """Fetch a one-line weather summary for Thiruvananthapuram."""
    response = requests.get(WEATHER_URL, timeout=10)
    response.raise_for_status()
    return response.text.strip()


def generate_ai_briefing(weather_summary: str) -> str:
    """Generate a context-aware morning briefing from the weather summary."""
    try:
        api_key = os.environ.get("AI_API_KEY")
        if not api_key:
            return FALLBACK_BRIEFING

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.environ.get("AI_MODEL", "gemini-3.5-flash"),
            contents=f"Weather context: {weather_summary}",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are Pulse, a concise morning briefing assistant. "
                    "Use the provided real-time Thiruvananthapuram weather "
                    "context to generate a sharp, highly specific, exactly "
                    "3-sentence morning briefing. Do not mention that you are "
                    "an AI."
                )
            ),
        )
        return response.text.strip() or FALLBACK_BRIEFING
    except Exception as exc:
        print(f"AI briefing generation failed: {exc}")
        return FALLBACK_BRIEFING


def build_daily_summary() -> str:
    weather_summary = fetch_weather_summary()
    ai_briefing = generate_ai_briefing(weather_summary)

    return f"""Pulse Daily Summary

Weather:
{weather_summary}

Morning Briefing:
{ai_briefing}
"""


def main() -> None:
    summary = build_daily_summary()
    print(summary)
    OUTPUT_FILE.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
