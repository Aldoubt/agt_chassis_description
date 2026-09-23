from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    package_share = FindPackageShare("agt_robot_description")
    robot = LaunchConfiguration("robot")
    model = PathJoinSubstitution([
        package_share, "urdf", "robots", robot, "robot.urdf.xacro"])
    default_calibration = PathJoinSubstitution(
        [package_share, "config", "field_acceptance.yaml"]
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
        DeclareLaunchArgument("robot", default_value="bunker_v1", choices=["bunker_v1"]),
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
