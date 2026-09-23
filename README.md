# agt_robot_description

This is a corrected ROS 2 Humble-ready description derived from the supplied SolidWorks-to-URDF
export. It preserves the original CAD geometry and nominal MID360 mounting but separates the
legacy CAD coordinate system from ROS navigation frames.

## Main changes

- ROS 1/catkin -> ROS 2/ament_cmake.
- Package migrated from `tracked_chassis_description` to `agt_robot_description`.
- Correct TF direction: `base_footprint -> base_link`.
- Legacy SolidWorks `base` datum renamed semantically to `chassis_cad_link`.
- MID360 CAD mounting preserved under `lidar_mount_link`.
- Added a separate `lidar_link` calibration-residual layer.
- Added `livox_frame` and `imu_link` runtime compatibility frames.
- GNSS frame is fail-closed/disabled until an APC lever arm is known.
- High-resolution chassis STL is visual-only; collision uses a primitive box.
- All uncertain alignment values are centralized in one YAML and marked unverified.

## ROS 2 usage

Copy the package into a ROS 2 Humble workspace `src/`, then:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select agt_robot_description
source install/setup.bash
ros2 launch agt_robot_description display.launch.py robot:=bunker_v1
```

Use another calibration file when available:

```bash
ros2 launch agt_robot_description display.launch.py robot:=bunker_v1 \
  calibration_file:=/absolute/path/to/verified_alignment.yaml
```

## Important

The default `cad_alignment.initial_guess.yaml` is for visualization and calibration bootstrap only.
It must not be treated as a verified navigation extrinsic.

See `docs/CALIBRATION_WORKFLOW.md` and `docs/AGT_RUNTIME_INTEGRATION.md`.
