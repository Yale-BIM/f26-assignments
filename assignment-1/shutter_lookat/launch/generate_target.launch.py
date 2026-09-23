#!/usr/bin/env python3
"""Bring up the simulation and publish a simulated moving target in front of Shutter.

Runs start_sim.launch.py (MuJoCo + RViz) and adds the target generator on top:

    ros2 launch shutter_lookat start_sim.launch.py
    ros2 run shutter_lookat generate_target.py

MuJoCo owns the clock, so every node started here runs with use_sim_time:=true --
generate_target.py stamps its poses and markers with get_clock().now(), and its
publishing timer is driven by the same clock. Without it the target would be
stamped in wall time while the robot's transforms carry simulated time, and RViz
would drop the marker as an extrapolation error.

RViz comes from start_sim.launch.py, which is handed config/lookat-target.rviz
here -- that config already subscribes to /target_marker, so the target shows up
without a second RViz.

Usage:
    ros2 launch shutter_lookat generate_target.launch.py
    ros2 launch shutter_lookat generate_target.launch.py target_x_plane:=0.5 publish_rate:=1
    ros2 launch shutter_lookat generate_target.launch.py look_forward:=False
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare launch arguments
    look_forward_arg = DeclareLaunchArgument(
        'look_forward',
        default_value='True',
        description='Make shutter look forward?'
    )

    target_x_plane_arg = DeclareLaunchArgument(
        'target_x_plane',
        default_value='1.5',
        description='X plane position for target'
    )

    target_radius_arg = DeclareLaunchArgument(
        'target_radius',
        default_value='0.05',
        description='Radius of the target'
    )

    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='30',
        description='Publishing rate for target'
    )

    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='false',
        description='Suppress the MuJoCo Simulate window.'
    )

    sim_speed_factor_arg = DeclareLaunchArgument(
        'sim_speed_factor',
        default_value='1.0',
        description='1.0 is real time; higher runs the physics faster than real time.'
    )

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([
            FindPackageShare('shutter_lookat'),
            'config',
            'lookat-target.rviz'
        ]),
        description='RViz display config passed to start_sim.launch.py. Defaults '
                    'to the lookat-target config in this package.'
    )

    # MuJoCo simulation plus RViz. This brings up robot_state_publisher and the
    # joint_state_broadcaster through ros2_control, so /joint_states and the TF
    # tree are already published -- a joint_state_publisher here would fight them
    # for /joint_states. It also publishes /clock and is the time source for the
    # whole run.
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('shutter_lookat'),
                'launch',
                'start_sim.launch.py'
            ])
        ]),
        launch_arguments={
            'headless': LaunchConfiguration('headless'),
            'sim_speed_factor': LaunchConfiguration('sim_speed_factor'),
            'rviz_config': LaunchConfiguration('rviz_config'),
        }.items()
    )

    # Generate target node
    generate_target_node = Node(
        package='shutter_lookat',
        executable='generate_target.py',
        name='generate_target',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'x_value': LaunchConfiguration('target_x_plane'),
            'radius': LaunchConfiguration('target_radius'),
            'publish_rate': LaunchConfiguration('publish_rate')
        }]
    )

    # Look forward node (conditional)
    look_forward_node = Node(
        package='shutter_lookat',
        executable='look_forward.py',
        name='look_forward',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('look_forward'))
    )

    return LaunchDescription([
        look_forward_arg,
        target_x_plane_arg,
        target_radius_arg,
        publish_rate_arg,
        headless_arg,
        sim_speed_factor_arg,
        rviz_config_arg,
        sim_launch,
        generate_target_node,
        look_forward_node,
    ])
