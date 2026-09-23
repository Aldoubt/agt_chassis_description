import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree

import jsonschema
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
    for key in ('xacro', 'calibration'):
        assert (ROOT / profile['description'][key]).is_file()


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
