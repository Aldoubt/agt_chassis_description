"""Sole robot_state_publisher owner; model/calibration come from one profile."""
from pathlib import Path
import math
import yaml
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _description(context):
    value=lambda name: LaunchConfiguration(name).perform(context)
    share=Path(get_package_share_directory('agt_robot_description'))
    profiles=Path(value('profiles_dir')).expanduser() if value('profiles_dir') else share/'config/robot_profiles'
    robot=value('robot')
    if not robot or Path(robot).name != robot or robot in ('.','..'):
        raise RuntimeError('one exact robot profile id required')
    profile=yaml.safe_load((profiles/(robot+'.yaml')).read_text())
    if profile.get('robot_id') != robot:
        raise RuntimeError('Robot Profile identity mismatch')
    def resolve(name):
        path=Path(profile['description'][name])
        if path.is_absolute() or '..' in path.parts:
            raise RuntimeError('description files must remain inside agt_robot_description')
        return share/path
    model=resolve('xacro')
    calibration=Path(value('calibration_file')).expanduser() if value('calibration_file') else resolve('calibration')
    if not model.is_file() or not calibration.is_file():
        raise RuntimeError('selected model and calibration files must exist')
    if robot != 'bunker_v1':
        cfg=yaml.safe_load(calibration.read_text())
        if cfg.get('calibration_verified') is not True or cfg.get('robot_id') != robot:
            raise RuntimeError('non-baseline vehicle TF requires its own measured verified calibration')
        if not str(cfg.get('verified_by','')).strip():
            raise RuntimeError('non-baseline calibration requires verified_by')
        if 'generic_tracked' in model.parts:
            if not isinstance(cfg.get('base_link_z'),(int,float)) or not math.isfinite(cfg['base_link_z']):
                raise RuntimeError('generic tracked base_link_z requires a finite measured value')
            for section,keys in (('collision_proxy',('size','origin_xyz','origin_rpy')),
                                 ('base_link_to_lidar',('xyz','rpy')),('lidar_to_imu',('xyz','rpy'))):
                for key in keys:
                    values=cfg.get(section,{}).get(key)
                    if (not isinstance(values,list) or len(values)!=3 or
                            any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in values)):
                        raise RuntimeError(f'measured {section}.{key} vector required')
                    if key=='size' and min(values)<=0:
                        raise RuntimeError('positive collision dimensions required')
            if any(profile['frames'].get(key)!=name for key,name in
                    {'base':'base_link','footprint':'base_footprint','lidar':'lidar_link','imu':'imu_link'}.items()):
                raise RuntimeError('generic tracked model frame names must match its profile')
    xml=xacro.process_file(str(model),mappings={'calibration_file':str(calibration)}).toxml()
    return [Node(package='robot_state_publisher',executable='robot_state_publisher',
                 name='robot_state_publisher',output='screen',parameters=[{
                     'robot_description':xml,'use_sim_time':value('use_sim_time').lower()=='true'}])]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot',default_value='bunker_v1'),
        DeclareLaunchArgument('profiles_dir',default_value=''),
        DeclareLaunchArgument('calibration_file',default_value=''),
        DeclareLaunchArgument('use_sim_time',default_value='false'),
        OpaqueFunction(function=_description),
    ])
