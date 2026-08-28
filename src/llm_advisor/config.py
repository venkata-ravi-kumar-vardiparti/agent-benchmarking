"""Environment and configuration loading."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    default_model: str


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        default_model=os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
    )
