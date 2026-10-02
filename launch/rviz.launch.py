"""Standalone RViz UI; it does not publish TF or navigation state."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _rviz(context):
    config = LaunchConfiguration('config_file').perform(context).strip()
    arguments = ['-d', config] if config else []
    return [Node(package='rviz2', executable='rviz2', name='agt_description_rviz',
                 output='screen', arguments=arguments)]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('config_file', default_value=''),
        OpaqueFunction(function=_rviz),
    ])
