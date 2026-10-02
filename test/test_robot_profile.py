import copy
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / 'config' / 'robot_profiles'


def test_bunker_profile_and_physical_sources():
    profile = yaml.safe_load((PROFILE_DIR / 'bunker_v1.yaml').read_text())
    schema = json.loads((PROFILE_DIR / 'schema.json').read_text())
    jsonschema.validate(profile, schema)
    assert profile['robot_id'] == 'bunker_v1'
    assert profile['terrain']['max_slope_deg'] is None
    assert profile['geometry']['width'] is None
    assert profile['geometry']['length'] is None
    assert profile['capabilities']['manipulation'] is False
    assert profile['base'] == {
        'type': 'tracked',
        'driver': 'bunker_base',
        'kinematics': 'skid_steer',
        'command_interface': 'twist',
        'odom_source': '/wheel/odom',
        'publish_odom_tf': False,
        'control_rate_hz': 50,
        'rotate_in_place': True,
    }
    assert profile['motion']['max_linear_velocity'] == 0.55
    assert profile['motion']['max_angular_velocity'] == 0.65
    for key in ('xacro', 'calibration'):
        assert (ROOT / profile['description'][key]).is_file()


def _synthetic_ackermann_profile():
    """Unit-test-only geometry. These values are not a real robot profile."""
    profile = yaml.safe_load((PROFILE_DIR / 'bunker_v1.yaml').read_text())
    profile = copy.deepcopy(profile)
    profile['base'].update({
        'kinematics': 'ackermann',
        'rotate_in_place': False,
        'ackermann': {
            'wheelbase_m': 1.2,
            'steering_angle_min_rad': -0.55,
            'steering_angle_max_rad': 0.55,
            'max_steering_rate_radps': 0.8,
            'minimum_turning_radius_m': 1.95,
        },
    })
    profile['geometry'].update({'width': 0.9, 'length': 1.6, 'safety_margin': 0.05})
    profile['motion'].update({'max_linear_velocity': 1.0, 'max_angular_velocity': 0.4})
    return profile


def test_ackermann_profile_requires_explicit_test_geometry_and_motion_limits():
    """Synthetic values exercise the schema only; no physical profile is added."""
    schema = json.loads((PROFILE_DIR / 'schema.json').read_text())
    jsonschema.validate(_synthetic_ackermann_profile(), schema)


@pytest.mark.parametrize('mutate', [
    lambda p: p['base']['ackermann'].pop('wheelbase_m'),
    lambda p: p['base']['ackermann'].pop('steering_angle_min_rad'),
    lambda p: p['base']['ackermann'].pop('steering_angle_max_rad'),
    lambda p: p['base']['ackermann'].pop('max_steering_rate_radps'),
    lambda p: p['base']['ackermann'].pop('minimum_turning_radius_m'),
    lambda p: p['base'].update(rotate_in_place=True),
    lambda p: p['geometry'].update(width=None),
    lambda p: p['geometry'].update(length=None),
    lambda p: p['motion'].update(max_linear_velocity=None),
    lambda p: p['motion'].update(max_angular_velocity=None),
])
def test_ackermann_missing_or_unsafe_values_fail_closed(mutate):
    schema = json.loads((PROFILE_DIR / 'schema.json').read_text())
    profile = _synthetic_ackermann_profile()
    mutate(profile)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(profile, schema)


def test_unknown_kinematics_and_competing_odom_tf_are_rejected():
    schema = json.loads((PROFILE_DIR / 'schema.json').read_text())
    profile = yaml.safe_load((PROFILE_DIR / 'bunker_v1.yaml').read_text())
    profile['base']['kinematics'] = 'unresolved'
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(profile, schema)
    profile['base']['kinematics'] = 'skid_steer'
    profile['base']['publish_odom_tf'] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(profile, schema)


def test_bunker_xacro_keeps_required_frames_and_calibration():
    profile = yaml.safe_load((PROFILE_DIR / 'bunker_v1.yaml').read_text())
    result = subprocess.run(
        ['xacro', str(ROOT / profile['description']['xacro']),
         f"calibration_file:={ROOT / profile['description']['calibration']}"],
        check=True, text=True, capture_output=True)
    robot = ElementTree.fromstring(result.stdout)
    links = {node.attrib['name'] for node in robot.findall('link')}
    assert {'base_footprint', 'base_link', 'lidar_link', 'imu_link'} <= links
    joints = {node.attrib['name']: node for node in robot.findall('joint')}
    assert joints['base_footprint_to_base_link'].find('origin').attrib['xyz'] == '0 0 0.2'
    assert joints['chassis_cad_to_lidar_mount'].find('origin').attrib['rpy'] == (
        '0.0 0.226892802759063 0.0')
