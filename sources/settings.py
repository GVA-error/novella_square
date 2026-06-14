from dataclasses import dataclass
from configparser import ConfigParser


@dataclass
class Settings:
    capture_hotkey: str
    exit_hotkey: str
    language: str
    start_hidden: bool
    border_color: str
    border_width: int


def load_settings():
    config = ConfigParser()
    config.read("config.ini")

    return Settings(
        capture_hotkey=config.get("hotkeys", "capture", fallback="alt"),
        exit_hotkey=config.get("hotkeys", "exit", fallback="f11"),
        language=config.get("ocr", "language", fallback="japan"),
        start_hidden=config.getboolean("app", "start_hidden", fallback=True),
        border_color=config.get(
            "overlay",
            "border_color",
            fallback="#ff00ff"
        ),
        border_width=config.getint(
            "overlay",
            "border_width",
            fallback=2
        )
    )

def save_settings(settings: Settings):
    config = ConfigParser()
    config["hotkeys"] = {
        "capture": settings.capture_hotkey,
        "exit": settings.exit_hotkey,
    }
    config["ocr"] = {
        "language": settings.language,
    }
    config["app"] = {
        "start_hidden": str(settings.start_hidden).lower(),
    }
    config["overlay"] = {
        "border_color": settings.border_color,
        "border_width": str(settings.border_width),
    }

    with open("config.ini", "w", encoding="utf-8") as f:
        config.write(f)