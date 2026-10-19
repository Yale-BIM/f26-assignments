cmake_minimum_required(VERSION 3.8)
project(shutter_behavior_cloning)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

# Install Python scripts. Globbed rather than listed because the relevant python
# files change as students work on the assignment (e.g., learn_policy.py).
# CONFIGURE_DEPENDS re-runs the glob at build time, so a newly created script is installed
# by the next `colcon build` without a manual reconfigure.
# Helper modules (look_at_solver.py, servo_joint_client.py, transformations.py) are installed
# next to the nodes, so that the nodes can import them.
file(GLOB PYTHON_SCRIPT_FILES
  CONFIGURE_DEPENDS
  LIST_DIRECTORIES false
  "${CMAKE_CURRENT_SOURCE_DIR}/scripts/*.py"
)
install(PROGRAMS
  ${PYTHON_SCRIPT_FILES}
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
  FILES_MATCHING PATTERN "*.launch.py"
)

# Install data directory (where the expert saves state-action pairs by default)
install(DIRECTORY data
  DESTINATION share/${PROJECT_NAME}/
)

# Test dependencies
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
