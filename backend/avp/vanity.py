"""Deterministic vanity classification; NOT provisioning or number assignment."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from enum import Enum


E164_RE = re.compile(r"^\+[1-9][0-9]{1,14}$")


class NumberTier(str, Enum):
    PLATINUM = "PLATINUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    STANDARD = "STANDARD"


@dataclass(frozen=True)
class NumberAssessment:
    e164: str
    tier: NumberTier
    score: int
    entropy_bits: float
    unique_digits: int

    def as_dict(self) -> dict:
        return asdict(self)


def require_e164(number: str) -> str:
    if not E164_RE.fullmatch(number):
        raise ValueError("E.164 must begin with + and contain 2..15 digits")
    return number


def _longest_consecutive(digits: str) -> int:
    best = 1
    current = 1
    for a, b in zip(digits, digits[1:]):
        if int(b) - int(a) in (-1, 1) and (
            current == 1 or int(b) - int(a) == prev_step
        ):
            current += 1
        else:
            current = 1
        prev_step = int(b) - int(a)
        best = max(best, current)
    return best


def evaluate_number(e164: str) -> NumberAssessment:
    digits = require_e164(e164)[1:]
    counts = Counter(digits)
    length = len(digits)
    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )
    platinum = bool(re.search(r"(\d)\1{5,}", digits)) or _longest_consecutive(digits) >= 6
    gold = bool(
        re.search(r"(\d{3})\1", digits)
        or re.search(r"(\d{2})\1{3,}", digits)
        or re.search(r"(\d)\1{3,}", digits)
    )
    if platinum:
        tier, score = NumberTier.PLATINUM, 100
    elif gold:
        tier, score = NumberTier.GOLD, 80
    elif len(counts) <= 3:
        tier, score = NumberTier.SILVER, 50
    else:
        tier, score = NumberTier.STANDARD, 10
    return NumberAssessment(
        e164=e164,
        tier=tier,
        score=score,
        entropy_bits=round(entropy, 4),
        unique_digits=len(counts),
    )
