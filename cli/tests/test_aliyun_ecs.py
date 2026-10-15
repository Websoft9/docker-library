from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone

import pytest
from typer.testing import CliRunner

from libs import aliyun_ecs, ops


runner = CliRunner()


CONFIG = {
    "provider": "aliyun",
    "region": "cn-hongkong",
    "instance": {
        "name_prefix": "libs-test",
        "type": "ecs.g7.large",
        "spot_strategy": "SpotAsPriceGo",
        "spot_duration": 0,
        "internet_max_bandwidth_out": 100,
        "key_pair_name": "websoft9_auto",
    },
    "system_disk": {
        "category": "cloud_essd",
        "min_size_gib": 20,
        "max_size_gib": 500,
        "default_size_gib": 200,
    },
    "release": {"default_hours": 10, "min_hours": 1, "max_hours": 168},
    "network": {
        "security_group_id": "sg-j6c7epgwcech14ofdt5l",
        "vswitch_id": "vsw-j6cpor7vbblzas6ui2pkf",
    },
    "image": {"owner_alias": "marketplace", "product_code": "cmjj010728", "select": "latest"},
}


def _write_config(repo_fixture) -> None:
    (repo_fixture / "ci" / "cloud").mkdir(parents=True)
    (repo_fixture / "ci" / "cloud" / "aliyun-ecs.json").write_text(
        json.dumps(CONFIG), encoding="utf-8"
    )


def test_parse_duration_units():
    assert aliyun_ecs.parse_duration("90m") == timedelta(minutes=90)
    assert aliyun_ecs.parse_duration("10h") == timedelta(hours=10)
    assert aliyun_ecs.parse_duration("2d") == timedelta(days=2)
    assert aliyun_ecs.parse_duration("30") == timedelta(hours=30)
    with pytest.raises(aliyun_ecs.EcsError):
        aliyun_ecs.parse_duration("soon")


def test_auto_release_iso_uses_utc():
    now = datetime(2026, 10, 13, 1, 19, 0, tzinfo=timezone.utc)
    assert aliyun_ecs.auto_release_iso(timedelta(hours=10), now=now) == "2026-10-13T11:19:00Z"


def test_load_config_reads_repo_default(repo_fixture):
    _write_config(repo_fixture)
    config = aliyun_ecs.load_config()
    assert config["region"] == "cn-hongkong"
    assert config["system_disk"]["default_size_gib"] == 200


def test_load_config_rejects_missing(repo_fixture):
    with pytest.raises(aliyun_ecs.EcsError, match="config not found"):
        aliyun_ecs.load_config()


def test_validate_disk_size_bounds():
    aliyun_ecs.validate_disk_size(CONFIG, 200)
    with pytest.raises(aliyun_ecs.EcsError, match="below the minimum"):
        aliyun_ecs.validate_disk_size(CONFIG, 10)
    with pytest.raises(aliyun_ecs.EcsError, match="above the maximum"):
        aliyun_ecs.validate_disk_size(CONFIG, 999)


def test_resolve_image_selects_latest_product_match(monkeypatch):
    images = [
        {"ImageId": "m-old", "ProductCode": "cmjj010728", "ImageName": "old", "CreationTime": "2025-01-01T00:00:00Z"},
        {"ImageId": "m-new", "ProductCode": "cmjj010728", "ImageName": "new", "CreationTime": "2026-10-01T00:00:00Z"},
        {"ImageId": "m-other", "ProductCode": "other0001", "ImageName": "other", "CreationTime": "2027-01-01T00:00:00Z"},
    ]
    monkeypatch.setattr(aliyun_ecs, "list_marketplace_images", lambda *args, **kwargs: images)

    image = aliyun_ecs.resolve_image(CONFIG, key_id="id", key_secret="secret")

    assert image["image_id"] == "m-new"
    assert image["product_code"] == "cmjj010728"


def test_resolve_image_explicit_id_skips_lookup(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError("should not query the API")

    monkeypatch.setattr(aliyun_ecs, "list_marketplace_images", boom)
    image = aliyun_ecs.resolve_image(CONFIG, image_id="m-explicit")
    assert image == {"image_id": "m-explicit", "image_name": None, "product_code": None, "source": "explicit"}


def test_build_run_instances_params_includes_dynamic_fields():
    image = {"image_id": "m-j6caxlj97mf3l51d0wcz", "image_name": "WordPress", "product_code": "cmjj010728", "source": "marketplace"}
    params = aliyun_ecs.build_run_instances_params(
        CONFIG, image, disk_size_gib=300, auto_release_time="2026-10-13T11:19:00Z"
    )

    assert params["SystemDisk.Size"] == 300
    assert params["AutoReleaseTime"] == "2026-10-13T11:19:00Z"
    assert params["ImageId"] == "m-j6caxlj97mf3l51d0wcz"
    assert params["SpotStrategy"] == "SpotAsPriceGo"
    assert params["SecurityGroupId"] == "sg-j6c7epgwcech14ofdt5l"
    assert re.match(r"^libs-test-\d{6}$", params["InstanceName"])

    named = aliyun_ecs.build_run_instances_params(CONFIG, image, disk_size_gib=300, name="custom-name")
    assert named["InstanceName"] == "custom-name"


def test_generate_instance_name_uses_prefix():
    assert re.match(r"^libs-test-\d{6}$", aliyun_ecs.generate_instance_name("libs-test"))
    assert re.match(r"^libs-test-\d{6}$", aliyun_ecs.generate_instance_name())


def test_public_ips_collects_public_and_eip():
    instance = {
        "PublicIpAddress": {"IpAddress": ["1.2.3.4"]},
        "EipAddress": {"IpAddress": "5.6.7.8"},
    }
    assert aliyun_ecs.public_ips(instance) == ["1.2.3.4", "5.6.7.8"]


def test_wait_for_public_ip_returns_when_ready(monkeypatch):
    monkeypatch.setattr(
        aliyun_ecs,
        "describe_instance",
        lambda *args, **kwargs: {"Status": "Running", "PublicIpAddress": {"IpAddress": ["47.1.2.3"]}},
    )
    result = aliyun_ecs.wait_for_public_ip("i-1", "id", "secret", "cn-hongkong", timeout=1)
    assert result["public_ip"] == "47.1.2.3"
    assert result["pending"] is False


def test_wait_for_public_ip_times_out(monkeypatch):
    monkeypatch.setattr(
        aliyun_ecs,
        "describe_instance",
        lambda *args, **kwargs: {"Status": "Starting", "PublicIpAddress": {"IpAddress": []}},
    )
    result = aliyun_ecs.wait_for_public_ip("i-1", "id", "secret", "cn-hongkong", timeout=0)
    assert result["pending"] is True
    assert result["public_ip"] is None
    assert result["status"] == "Starting"


def test_run_instances_parses_instance_ids(monkeypatch):
    monkeypatch.setattr(
        aliyun_ecs,
        "_call",
        lambda *args, **kwargs: {"RequestId": "req-1", "InstanceIdSets": {"InstanceIdSet": ["i-1"]}},
    )
    result = aliyun_ecs.run_instances({"RegionId": "cn-hongkong"}, "id", "secret")
    assert result == {"request_id": "req-1", "instance_ids": ["i-1"]}


def test_create_command_dry_run_does_not_call_api(repo_fixture, monkeypatch):
    _write_config(repo_fixture)

    def boom(*args, **kwargs):
        raise AssertionError("should not call the API during --dry-run")

    monkeypatch.setattr(ops.aliyun_ecs, "run_instances", boom)

    result = runner.invoke(
        ops.app,
        [
            "create-aliyun-ecs",
            "--image-id",
            "m-explicit",
            "--disk-size",
            "300",
            "--release-in",
            "10h",
            "--dry-run",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dry_run"] is True
    assert payload["disk_size_gib"] == 300
    assert payload["image_id"] == "m-explicit"


def test_create_command_interactive_abort(repo_fixture, monkeypatch):
    _write_config(repo_fixture)
    monkeypatch.setattr(
        ops.aliyun_ecs,
        "resolve_image",
        lambda *args, **kwargs: {"image_id": "m-x", "image_name": "img", "source": "marketplace"},
    )
    called = []
    monkeypatch.setattr(ops.aliyun_ecs, "run_instances", lambda *args, **kwargs: called.append(True))

    result = runner.invoke(ops.app, ["create-aliyun-ecs"], input="300\n10\nn\n")

    assert result.exit_code == 0, result.output
    assert "Aborted" in result.output
    assert called == []


def test_create_command_outputs_public_ip(repo_fixture, monkeypatch):
    _write_config(repo_fixture)
    monkeypatch.setattr(
        ops.aliyun_ecs,
        "run_instances",
        lambda *args, **kwargs: {"request_id": "req-1", "instance_ids": ["i-1"]},
    )
    monkeypatch.setattr(
        ops.aliyun_ecs,
        "wait_for_public_ip",
        lambda *args, **kwargs: {
            "instance_id": "i-1",
            "public_ip": "47.9.9.9",
            "public_ips": ["47.9.9.9"],
            "status": "Running",
            "pending": False,
        },
    )

    result = runner.invoke(
        ops.app,
        ["create-aliyun-ecs", "--image-id", "m-x", "--disk-size", "100", "--release-in", "1h", "--yes", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["public_ip"] == "47.9.9.9"
    assert payload["instance_ids"] == ["i-1"]
    assert payload["action"] == "created"


def test_create_command_rejects_out_of_range_disk(repo_fixture):
    _write_config(repo_fixture)

    result = runner.invoke(
        ops.app,
        ["create-aliyun-ecs", "--image-id", "m-explicit", "--disk-size", "9999", "--release-in", "10h", "--yes", "--json"],
    )

    assert result.exit_code == 2
    assert "above the maximum" in (result.output + (result.stderr or ""))
