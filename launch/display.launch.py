"""Compatibility aggregate for robot description and optional RViz."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    share = FindPackageShare('agt_robot_description')
    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='bunker_v1', choices=['bunker_v1']),
        DeclareLaunchArgument('calibration_file', default_value=PathJoinSubstitution([
            share, 'config', 'field_acceptance.yaml'])),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                share, 'launch', 'description.launch.py'])),
            launch_arguments={
                'robot': LaunchConfiguration('robot'),
                'calibration_file': LaunchConfiguration('calibration_file'),
            }.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                share, 'launch', 'rviz.launch.py'])),
            condition=IfCondition(LaunchConfiguration('start_rviz'))),
    ])
