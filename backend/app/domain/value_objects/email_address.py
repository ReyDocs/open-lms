from dataclasses import dataclass
import re


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self):
        email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_regex, self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    def __str__(self) -> str:
        return self.value.lower().strip()
