#!/usr/bin/env python3
# Public tests for CPSC-4590/5590 Assignment 1 - Part II

PKG = "shutter_lookat_public_tests"
NAME = 'test_publish_target'

import sys
import unittest
import tf2_ros

import rclpy
from rclpy.parameter import Parameter
import pytest
import time

from utils import inspect_rostopic_info

import launch
import launch_ros
import launch_testing
import launch_testing.actions
from launch_testing.actions import ReadyToTest
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_test_description():
    # Bring up the MuJoCo simulation. This is the same start_sim.launch.py that
    # generate_target.launch.py runs for the assignment, only without RViz or the
    # MuJoCo window, which the tests have no use for and which let them run over
    # ssh and on CI. MuJoCo owns the clock here -- it publishes
    # /clock and starts its own nodes with use_sim_time:=true -- which is why
    # every node started below sets use_sim_time as well.
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('shutter_lookat'),
                'launch',
                'start_sim.launch.py'
            ])
        ]),
        launch_arguments={
            'rviz': 'false',
            'headless': 'true',
            'face': 'false',
        }.items()
    )

    # Look forward node. It commands joint_4 through ros2_control's
    # joint_group_controller, so it only does anything once the simulation's
    # controllers have been spawned.
    look_forward_node = Node(
        package='shutter_lookat',
        executable='look_forward.py',
        name='look_forward',
        parameters=[{'use_sim_time': True}]
    )

    # Generate target node
    generate_target_node = Node(
        package='shutter_lookat',
        executable='generate_target.py',
        name='generate_target',
        output='screen',
        parameters=[{
            'x_value': 1.5,
            'radius': 0.05,
            'use_sim_time': True,
            'publish_rate': 30
        }]
    )

    # Student's code node
    publish_target_node = Node(
        package='shutter_lookat',
        executable='publish_target_relative_to_realsense_camera.py',
        name='publish_target_relative_to_realsense_camera',
        parameters=[{'use_sim_time': True}],
        # Surfaced so that a failing test shows the node's own errors
        # and warnings rather than only the assertion that failed.
        output='screen'
    )

    return (
        LaunchDescription(
            [
                sim_launch,
                look_forward_node,
                generate_target_node,
                publish_target_node,
                # launch_testing gives the launch description 15 seconds to signal that it
                # is ready, so this cannot be used to wait out the simulation's startup --
                # each test below polls for what it needs instead.
                TimerAction(
                    period=2.0,
                    actions=[ReadyToTest()]
                ),
            ]
        ), {},
    )


class TestPublishTarget(unittest.TestCase):
    """
    Public tests for publish_target_relative_to_realsense_camera.py
    """

    @classmethod
    def setUpClass(cls):
        """Initialize ROS for the test class."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shutdown ROS after the test class."""
        rclpy.shutdown()

    def setUp(self):
        """Create a node for each test."""
        self.node = rclpy.create_node(NAME, parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.node_name = "/publish_target_relative_to_realsense_camera"   # name of the node when launched for the tests
        self.target_topic = "/target"                                    # target topic
        self.target_frame = "target"                                     # target frame
        self.robot_frame = "shutter_base_footprint"                      # frame the target pose comes in

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self.node)

    def tearDown(self):
        """Destroy the node after each test."""
        self.node.destroy_node()
        
    def test_node_connections(self):
        """
        Check the node's connections
        """
        success = False
        timeout_t = time.time() + 45  # 45 seconds in the future
        
        while rclpy.ok() and not success and time.time() < timeout_t:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if inspect_rostopic_info(self.node_name):
                success = True
                break
            time.sleep(0.1)

        self.assertTrue(success, "Failed to verify that the node publish_target_relative_to_realsense_camera.py "
                                 "subscribes to the {} topic".format(self.target_topic))
        print("Verified that the publish_target_relative_to_realsense_camera.py node subscribes to the {} topic".
              format(self.target_topic))

    def test_frame_exists(self):
        """
        Check that the target frame exists in the tf tree
        """
        t = None        # transform
        err = None      # error
        timeout_t = time.time() + 60  # 60 seconds in the future
        exceeded_time = False

        # Wait patiently for a transform. The deadline is part of the loop
        # condition rather than a check at the bottom of the body: every lookup
        # failure below is an expected way for the target frame to be missing
        # while the simulation is still coming up, and a deadline checked only
        # after a successful lookup would never be reached if it never succeeds.
        while rclpy.ok() and t is None and time.time() < timeout_t:
            rclpy.spin_once(self.node, timeout_sec=1.0)
            try:
                t = self.tf_buffer.lookup_transform(self.robot_frame,
                                                    self.target_frame,
                                                    rclpy.time.Time(),
                                                    timeout=rclpy.duration.Duration(seconds=1.0))  # wait for 1 second
            except (tf2_ros.LookupException,
                    tf2_ros.ConnectivityException,
                    tf2_ros.ExtrapolationException) as e:
                err = e

        if t is None:
            exceeded_time = True

        if err is not None:
            err_str = "Got error: {}".format(err)
        else:
            err_str = ""

        self.assertIsNotNone(t, f"Failed to find a transformation between {self.robot_frame} and {self.target_frame} "
                                f"(waited for {time.time()-timeout_t} secs / timeout: {exceeded_time}).{err_str}\n"
                                f"Check how the node is publishing the transform for the target.")

        print("Success. Found the frame {} in the tf tree!".format(self.target_frame))
