from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AppConfig:
    download_dir: str = "Downloads"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    cleanup_max_age: int = 60
    allowed_extensions: List[str] = field(
        default_factory=lambda: ["mp4", "mp3", "wav", "webm"]
    )
