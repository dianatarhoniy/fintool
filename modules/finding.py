from dataclasses import dataclass


@dataclass
class Finding:
    check: str
    severity: str
    title: str
    evidence: str