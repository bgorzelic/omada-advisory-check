import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from omada_advisory_check import BELOW, OK, UNKNOWN, check, load_fixed, parse_fw

FIXED = load_fixed()


def test_parse():
    assert parse_fw("2.4.4 Build 20260630 Rel.14398") == ((2, 4, 4), 20260630)
    assert parse_fw("garbage") is None


def test_below_fixed():
    assert check("ER605", "v2", "2.4.3 Build 20260101 Rel.1", FIXED)[0] == BELOW


def test_exact_and_newer():
    assert check("ER605", "2", "2.4.4 Build 20260630 Rel.14398", FIXED)[0] == OK
    assert check("ER605", "2", "2.5.0 Build 20261001 Rel.1", FIXED)[0] == OK


def test_same_version_older_build():
    assert check("ER605", "2", "2.4.4 Build 20260601 Rel.1", FIXED)[0] == BELOW


def test_multi_digit_not_lexical():
    assert check("ER706W", "1", "1.2.9 Build 20260101 Rel.1", FIXED)[0] == BELOW


def test_unknown_model_never_clean():
    assert check("ER9999", "1", "9.9.9 Build 20269999 Rel.1", FIXED)[0] == UNKNOWN


def test_unparseable_firmware_unknown():
    assert check("ER605", "2", "2.4.4", FIXED)[0] == UNKNOWN
