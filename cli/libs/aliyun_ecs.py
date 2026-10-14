from __future__ import annotations

import json
import random
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from libs import aliyun_rpc, credentials
from libs.repo import repo_path

ECS_VERSION = "2014-05-26"
ECS_ENDPOINT = "https://ecs.aliyuncs.com/"
DEFAULT_CONFIG = "ci/cloud/aliyun-ecs.json"
DEFAULT_NAME_PREFIX = "libs-test"
DEFAULT_WAIT_TIMEOUT = 180
POLL_INTERVAL = 5
PROVIDER = "aliyun"
ACCESS_KEY_ID_ENV = "ALIYUN_ACCESS_KEY_ID"
ACCESS_KEY_SECRET_ENV = "ALIYUN_ACCESS_KEY_SECRET"
PAGE_SIZE = 100

_DURATION_RE = re.compile(r"^\s*(\d+)\s*([smhd]?)\s*$", re.IGNORECASE)


class EcsError(RuntimeError):
    pass


def config_path(explicit: str | None = None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = repo_path(explicit)
        return path
    return repo_path(DEFAULT_CONFIG)


def load_config(explicit: str | None = None) -> dict:
    path = config_path(explicit)
    if not path.exists():
        raise EcsError(f"config not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise EcsError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(data, dict):
        raise EcsError(f"config must be a JSON object: {path}")
    data["_config_path"] = str(path)
    return data


def resolve_credentials(
    access_key_id: str | None = None,
    access_key_secret: str | None = None,
    env_file: str | None = None,
) -> tuple[str | None, str | None]:
    return (
        credentials.resolve_secret(ACCESS_KEY_ID_ENV, PROVIDER, access_key_id, env_file),
        credentials.resolve_secret(ACCESS_KEY_SECRET_ENV, PROVIDER, access_key_secret, env_file),
    )


def disk_bounds(config: dict, disk_size_gib: int | None = None) -> tuple[int | None, int | None]:
    disk = config.get("system_disk") or {}
    return disk.get("min_size_gib"), disk.get("max_size_gib")


def default_disk_size(config: dict) -> int | None:
    return (config.get("system_disk") or {}).get("default_size_gib")


def validate_disk_size(config: dict, disk_size_gib: int) -> None:
    low, high = disk_bounds(config)
    if low is not None and disk_size_gib < int(low):
        raise EcsError(f"disk size {disk_size_gib} GiB is below the minimum {low} GiB")
    if high is not None and disk_size_gib > int(high):
        raise EcsError(f"disk size {disk_size_gib} GiB is above the maximum {high} GiB")


def release_hours(config: dict) -> tuple[int, int, int]:
    release = config.get("release") or {}
    low = int(release.get("min_hours", 1))
    high = int(release.get("max_hours", 168))
    default = int(release.get("default_hours", low))
    return low, high, default


def parse_duration(value: str) -> timedelta:
    match = _DURATION_RE.match(str(value))
    if not match:
        raise EcsError(f"invalid duration {value!r}; use e.g. 90m, 10h, 2d")
    amount = int(match.group(1))
    unit = (match.group(2) or "h").lower()
    if amount <= 0:
        raise EcsError(f"duration must be positive: {value!r}")
    factors = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return timedelta(seconds=amount * factors[unit])


def auto_release_iso(duration: timedelta, now: datetime | None = None) -> str:
    base = now or datetime.now(timezone.utc)
    return (base + duration).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _call(action: str, params: dict, key_id: str, key_secret: str, endpoint: str = ECS_ENDPOINT) -> dict:
    try:
        return aliyun_rpc.rpc_call(
            action,
            params,
            key_id,
            key_secret,
            version=ECS_VERSION,
            endpoint=endpoint,
            label="Aliyun ECS",
        )
    except aliyun_rpc.AliyunApiError as error:
        raise EcsError(str(error)) from error


def list_marketplace_images(
    region: str,
    key_id: str,
    key_secret: str,
    *,
    owner_alias: str = "marketplace",
    name_keyword: str | None = None,
    endpoint: str = ECS_ENDPOINT,
) -> list[dict]:
    images: list[dict] = []
    page = 1
    while True:
        params: dict[str, object] = {
            "RegionId": region,
            "ImageOwnerAlias": owner_alias,
            "PageNumber": page,
            "PageSize": PAGE_SIZE,
        }
        if name_keyword:
            params["ImageName"] = name_keyword
        payload = _call("DescribeImages", params, key_id, key_secret, endpoint)
        chunk = (payload.get("Images") or {}).get("Image") or []
        images.extend(item for item in chunk if isinstance(item, dict))
        total = int(payload.get("TotalCount") or len(images))
        if not chunk or len(images) >= total:
            break
        page += 1
    return images


def select_latest(images: list[dict]) -> dict | None:
    if not images:
        return None
    return max(images, key=lambda item: (str(item.get("CreationTime") or ""), str(item.get("ImageId") or "")))


def resolve_image(
    config: dict,
    *,
    image_id: str | None = None,
    key_id: str | None = None,
    key_secret: str | None = None,
    endpoint: str = ECS_ENDPOINT,
) -> dict:
    if image_id:
        return {"image_id": image_id, "image_name": None, "product_code": None, "source": "explicit"}

    image_cfg = config.get("image") or {}
    product_code = image_cfg.get("product_code")
    if not product_code:
        raise EcsError("config image.product_code is required unless --image-id is given")
    if not key_id or not key_secret:
        raise EcsError("missing Aliyun credentials; run `make connector` and choose alibabacloud, or set ALIYUN_ACCESS_KEY_ID / ALIYUN_ACCESS_KEY_SECRET")

    images = list_marketplace_images(
        config["region"],
        key_id,
        key_secret,
        owner_alias=image_cfg.get("owner_alias", "marketplace"),
        name_keyword=image_cfg.get("name_keyword"),
        endpoint=endpoint,
    )
    matches = [item for item in images if str(item.get("ProductCode") or "").lower() == str(product_code).lower()]
    chosen = select_latest(matches) if image_cfg.get("select", "latest") == "latest" else (matches[0] if matches else None)
    if not chosen:
        raise EcsError(
            f"no available marketplace image found for product {product_code} in {config['region']}"
        )
    return {
        "image_id": chosen.get("ImageId"),
        "image_name": chosen.get("ImageName"),
        "product_code": product_code,
        "subscribed": chosen.get("IsSubscribed"),
        "source": "marketplace",
    }


def generate_instance_name(prefix: str | None = None) -> str:
    return f"{prefix or DEFAULT_NAME_PREFIX}-{random.randint(0, 999999):06d}"


def build_run_instances_params(
    config: dict,
    image: dict,
    *,
    disk_size_gib: int,
    auto_release_time: str | None = None,
    name: str | None = None,
) -> dict:
    instance = config.get("instance") or {}
    disk = config.get("system_disk") or {}
    network = config.get("network") or {}

    params: dict[str, object] = {
        "RegionId": config["region"],
        "InstanceName": name or generate_instance_name(instance.get("name_prefix")),
        "ImageId": image["image_id"],
        "InstanceType": instance.get("type"),
        "SecurityGroupId": network.get("security_group_id"),
        "VSwitchId": network.get("vswitch_id"),
        "InternetMaxBandwidthOut": instance.get("internet_max_bandwidth_out", 0),
        "KeyPairName": instance.get("key_pair_name"),
        "SystemDisk.Category": disk.get("category", "cloud_essd"),
        "SystemDisk.Size": disk_size_gib,
        "Amount": 1,
    }
    spot_strategy = instance.get("spot_strategy")
    if spot_strategy:
        params["SpotStrategy"] = spot_strategy
        params["SpotDuration"] = instance.get("spot_duration", 0)
    if auto_release_time:
        params["AutoReleaseTime"] = auto_release_time
    return {key: value for key, value in params.items() if value is not None}


def run_instances(
    params: dict,
    key_id: str,
    key_secret: str,
    endpoint: str = ECS_ENDPOINT,
) -> dict:
    payload = _call("RunInstances", params, key_id, key_secret, endpoint)
    instance_ids = (payload.get("InstanceIdSets") or {}).get("InstanceIdSet") or []
    return {
        "request_id": payload.get("RequestId"),
        "instance_ids": instance_ids,
    }


def describe_instance(
    instance_id: str,
    key_id: str,
    key_secret: str,
    region: str,
    endpoint: str = ECS_ENDPOINT,
) -> dict | None:
    payload = _call(
        "DescribeInstances",
        {"RegionId": region, "InstanceIds": json.dumps([instance_id])},
        key_id,
        key_secret,
        endpoint,
    )
    instances = (payload.get("Instances") or {}).get("Instance") or []
    return instances[0] if instances else None


def public_ips(instance: dict) -> list[str]:
    public = (instance.get("PublicIpAddress") or {}).get("IpAddress") or []
    if isinstance(public, str):
        public = [public]
    ips = [ip for ip in public if ip]
    eip = (instance.get("EipAddress") or {}).get("IpAddress")
    if eip and eip not in ips:
        ips.append(eip)
    return ips


def wait_for_public_ip(
    instance_id: str,
    key_id: str,
    key_secret: str,
    region: str,
    *,
    timeout: int = DEFAULT_WAIT_TIMEOUT,
    interval: int = POLL_INTERVAL,
    endpoint: str = ECS_ENDPOINT,
) -> dict:
    deadline = time.monotonic() + max(timeout, 0)
    last: dict | None = None
    while True:
        instance = describe_instance(instance_id, key_id, key_secret, region, endpoint)
        if instance:
            last = instance
            ips = public_ips(instance)
            if ips:
                return {
                    "instance_id": instance_id,
                    "public_ip": ips[0],
                    "public_ips": ips,
                    "status": instance.get("Status"),
                    "pending": False,
                }
        if time.monotonic() >= deadline:
            return {
                "instance_id": instance_id,
                "public_ip": None,
                "public_ips": [],
                "status": (last or {}).get("Status"),
                "pending": True,
            }
        time.sleep(interval)
