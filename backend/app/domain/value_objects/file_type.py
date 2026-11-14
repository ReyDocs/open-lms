from dataclasses import dataclass
import os

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "pptx", "xlsx", "jpg", "jpeg", "png", "zip", "mp4", "mp3", "csv", "txt"
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


@dataclass(frozen=True)
class FileType:
    filename: str

    @property
    def extension(self) -> str:
        _, ext = os.path.splitext(self.filename)
        return ext.lstrip(".").lower()

    def is_allowed(self) -> bool:
        return self.extension in ALLOWED_EXTENSIONS
