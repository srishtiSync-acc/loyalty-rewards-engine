import json

import pytest

from loyalty_rewards.store import DataLoadError, load_dataset


def test_dataset_loads_and_hides_email_from_safe_view(tmp_path):
    dataset = load_dataset("data/members.json")
    assert dataset.rules.human_gate_redeem_over == 30000
    assert dataset.members[0].email is not None


def test_malformed_json_fails_explicitly(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(DataLoadError):
        load_dataset(path)
