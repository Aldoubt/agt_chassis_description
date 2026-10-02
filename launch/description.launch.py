"""Sole robot_state_publisher owner for the selected Robot Profile."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    share = FindPackageShare('agt_robot_description')
    robot = LaunchConfiguration('robot')
    xacro_file = PathJoinSubstitution([
        share, 'urdf', 'robots', robot, 'robot.urdf.xacro'])
    calibration = LaunchConfiguration('calibration_file')
    default_calibration = PathJoinSubstitution(
        [share, 'config', 'field_acceptance.yaml'])
    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='bunker_v1', choices=['bunker_v1']),
        DeclareLaunchArgument('calibration_file', default_value=default_calibration),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            name='robot_state_publisher', output='screen', parameters=[{
                'robot_description': ParameterValue(Command([
                    'xacro ', xacro_file, ' calibration_file:=', calibration]), value_type=str),
            }]),
    ])
