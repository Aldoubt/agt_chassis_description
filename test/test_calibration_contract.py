from pathlib import Path
import math
import yaml


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _config():
    return yaml.safe_load(
        (_root() / "config" / "cad_alignment.initial_guess.yaml").read_text(encoding="utf-8")
    )


def _field_acceptance_config():
    return yaml.safe_load(
        (_root() / "config" / "field_acceptance.yaml").read_text(encoding="utf-8")
    )


def test_initial_candidate_is_not_marked_verified():
    cfg = _config()
    assert cfg["calibration_verified"] is False
    assert cfg["candidate_only"] is True
    assert cfg["base_link_to_cad"]["verified"] is False
    assert cfg["lidar_mount_to_lidar"]["verified"] is False


def test_field_acceptance_is_explicit_and_preserves_the_accepted_geometry():
    cfg = _field_acceptance_config()
    initial = _config()
    assert cfg["calibration_verified"] is True
    assert cfg["candidate_only"] is False
    assert cfg["acceptance_scope"] == "stationary_relocalization"
    assert cfg["base_link_to_cad"]["verified"] is True
    assert cfg["cad_to_lidar_mount"]["verified"] is True
    assert cfg["lidar_mount_to_lidar"]["verified"] is True
    assert cfg["base_link_to_cad"]["xyz"] == initial["base_link_to_cad"]["xyz"]
    assert cfg["cad_to_lidar_mount"]["rpy"] == initial["cad_to_lidar_mount"]["rpy"]


def test_solidworks_lidar_nominal_is_preserved():
    cfg = _config()["cad_to_lidar_mount"]
    assert cfg["xyz"] == [0.158123575840648, 0.0, 0.103682276997015]
    assert cfg["rpy"] == [0.0, 0.226892802759063, 0.0]


def test_gnss_is_fail_closed_until_apc_is_measured():
    assert _config()["gnss"]["enabled"] is False


def test_collision_proxy_is_lightweight_nominal_bunker_body():
    size = _config()["collision_proxy"]["size"]
    assert size == [1.023, 0.778, 0.400]


def test_candidate_places_cad_bbox_ground_near_zero():
    cfg = _config()
    base_z = cfg["base_link_z"]
    cad_z = cfg["base_link_to_cad"]["xyz"][2]
    original_mesh_min_z = -0.823785841
    assert math.isclose(base_z + cad_z + original_mesh_min_z, 0.0, abs_tol=1e-6)
