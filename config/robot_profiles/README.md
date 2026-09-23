# Robot Profile contract

`bunker_v1.yaml` records the current field robot without changing any URDF
transform or motion limit. `null` means that a physical measurement or terrain
acceptance result is unavailable. The `source` entries point to the existing
authority for each copied value. Future profiles must have distinct `robot_id`
values and their own tested Xacro/calibration inputs.
