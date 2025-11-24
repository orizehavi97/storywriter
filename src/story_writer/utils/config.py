"""Configuration management."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment and config files."""

    # API Keys
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    # Paths
    data_dir: Path = Field(default=Path("data"))
    chapters_dir: Path = Field(default=Path("data/chapters"))
    memory_dir: Path = Field(default=Path("data/memory"))
    config_dir: Path = Field(default=Path("config"))

    # Debug
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_yaml_config(config_name: str, config_dir: Path = Path("config")) -> dict:
    """Load a YAML configuration file."""
    config_path = config_dir / f"{config_name}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_llm_config() -> dict:
    """Get LLM configuration."""
    return load_yaml_config("llm_config")


def get_style_guide() -> dict:
    """Get style guide configuration."""
    return load_yaml_config("style_guide")


def get_world_seed() -> dict:
    """Get world seed configuration."""
    return load_yaml_config("world_seed")
