# Robot Profile contract

`bunker_v1.yaml` records the current field robot without changing any URDF
transform or motion limit. `null` means that a physical measurement or terrain
acceptance result is unavailable. The `source` entries point to the existing
authority for each copied value. Future profiles must have distinct `robot_id`
values and their own tested Xacro/calibration inputs.

The `base` section also records the validated runtime interface: kinematics,
command type, odometry topic, odometry TF ownership, state publication rate and
whether the configured navigation stack permits in-place rotation. Chassis
drivers must set `publish_odom_tf: false`; the selected LIO adapter owns
`odom -> base_footprint`.

Ackermann data belongs in `base.ackermann` and is required by the schema only
for an Ackermann profile. Wheelbase, steering limits/rate, minimum turning
radius, footprint dimensions, safety margin and positive motion limits must be
explicit. There is intentionally no production Ackermann profile until real
vehicle measurements exist. Synthetic Ackermann numbers may appear only in
unit-test fixtures. YHS remains blocked and has no kinematic classification
until its actual protocol and chassis geometry are audited.
