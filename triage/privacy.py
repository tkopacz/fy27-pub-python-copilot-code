import re


EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\w)(?:\+48[ -]?)?\d{9}(?!\w)")
PESEL = re.compile(r"(?<!\w)\d{11}(?!\w)")


def redact(text: str) -> str:
    text = EMAIL.sub("[EMAIL]", text)
    text = PHONE.sub("[PHONE]", text)
    return PESEL.sub("[PESEL]", text)
