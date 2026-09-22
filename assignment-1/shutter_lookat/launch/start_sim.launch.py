#!/usr/bin/env python3
"""Bring up Shutter in MuJoCo with a face, plus RViz to look at it.

Equivalent to running these two commands by hand:

    ros2 launch shutter_bringup shutter_sim.launch.py face:=true
    ros2 run rviz2 rviz2 -d <shutter_lookat>/config/shutter-model.rviz

MuJoCo owns the clock here: shutter_sim.launch.py runs ros2_control inside
mujoco_ros2_control, which publishes /clock at the MJCF timestep and brings its
nodes up with use_sim_time:=true. Anything that joins the run has to take its
time from /clock too, or it timestamps and interpolates against the wall clock
while everything else uses simulated time. For RViz that shows up as TF
lookups failing ("extrapolation into the future") and a robot that will not
render, so use_sim_time is set for the nodes started here.

Usage:
    ros2 launch shutter_lookat start_sim.launch.py
    ros2 launch shutter_lookat start_sim.launch.py face:=false
    ros2 launch shutter_lookat start_sim.launch.py headless:=true
    ros2 launch shutter_lookat start_sim.launch.py rviz:=false
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    face_arg = DeclareLaunchArgument(
        'face', default_value='true',
        description="Render Shutter's face onto the head screen.")

    headless_arg = DeclareLaunchArgument(
        'headless', default_value='false',
        description='Suppress the MuJoCo Simulate window.')

    sim_speed_factor_arg = DeclareLaunchArgument(
        'sim_speed_factor', default_value='1.0',
        description='1.0 is real time; higher runs the physics faster than real time.')

    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Start RViz alongside the simulation.')

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([
            FindPackageShare('shutter_lookat'),
            'config',
            'shutter-model.rviz',
        ]),
        description='RViz display config. Defaults to the shutter-model config '
                    'in this package.')

    # MuJoCo simulation. It sets use_sim_time:=true on its own nodes and starts
    # publishing /clock, so it is the time source for the whole run.
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('shutter_bringup'),
                'launch',
                'shutter_sim.launch.py',
            ])
        ]),
        launch_arguments={
            'face': LaunchConfiguration('face'),
            'headless': LaunchConfiguration('headless'),
            'sim_speed_factor': LaunchConfiguration('sim_speed_factor'),
        }.items(),
    )

    # use_sim_time is required, not cosmetic: without it RViz stamps its TF
    # queries with wall time while the transforms carry simulated time.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        face_arg,
        headless_arg,
        sim_speed_factor_arg,
        rviz_arg,
        rviz_config_arg,
        simulation,
        rviz_node,
    ])
