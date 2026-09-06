from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    package_share = FindPackageShare("tracked_chassis_description")
    model = PathJoinSubstitution([package_share, "urdf", "tracked_chassis.urdf.xacro"])
    default_calibration = PathJoinSubstitution(
        [package_share, "config", "cad_alignment.initial_guess.yaml"]
    )

    calibration_file = LaunchConfiguration("calibration_file")
    start_rviz = LaunchConfiguration("start_rviz")

    robot_description = ParameterValue(
        Command([
            "xacro ", model,
            " calibration_file:=", calibration_file,
        ]),
        value_type=str,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "calibration_file",
            default_value=default_calibration,
            description="YAML containing CAD alignment and sensor calibration transforms",
        ),
        DeclareLaunchArgument("start_rviz", default_value="true"),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": robot_description}],
            output="screen",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            condition=IfCondition(start_rviz),
            output="screen",
        ),
    ])
