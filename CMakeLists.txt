cmake_minimum_required(VERSION 3.8)
project(tracked_chassis_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch meshes urdf docs
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_calibration_contract test/test_calibration_contract.py)
endif()

ament_package()
