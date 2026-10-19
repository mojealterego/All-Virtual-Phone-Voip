import pytest

from avp.vanity import NumberTier, evaluate_number, require_e164
from .conftest import CARRIER, TENANT_A, token


@pytest.mark.parametrize(
    ("number", "tier"),
    [
        ("+48501777777", NumberTier.PLATINUM),
        ("+48501456456", NumberTier.GOLD),
        ("+48123123123", NumberTier.GOLD),
        ("+48501293847", NumberTier.STANDARD),
    ],
)
def test_tier_examples(number, tier):
    result = evaluate_number(number)
    assert result.tier == tier
    assert result.score in (10, 50, 80, 100)
    assert result.entropy_bits >= 0


@pytest.mark.parametrize("number", ["48500123456", "+", "+0012", "+48 500 123 456", "+1" + "2" * 15])
def test_fail_invalid_e164(number):
    with pytest.raises(ValueError):
        require_e164(number)


def test_consecutive_rule():
    assert evaluate_number("+48123456789").tier == NumberTier.PLATINUM


def test_vanity_http_does_not_allocate_numbers(ctx):
    client, _ = ctx
    res = client.post(
        "/v1/vanity/classify",
        json={"e164": "+48501777777"},
        headers=token(TENANT_A),
    )
    assert res.status_code == 200
    assert res.json()["tier"] == "PLATINUM"
    assert "reservation_id" not in res.json()
    assert client.post(
        "/v1/vanity/classify",
        json={"e164": "+48501777777"},
        headers=token(CARRIER),
    ).status_code == 403
