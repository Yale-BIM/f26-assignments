#!/usr/bin/env python3
# Public tests for CPSC-4590/5590 Assignment 1 - Part IV

PKG = "shutter_lookat_public_tests"
NAME = 'test_fancy_virtual_camera'

import sys
import unittest
import time
import numpy as np

import rclpy
from rclpy.parameter import Parameter
import pytest
from sensor_msgs.msg import CameraInfo
from sensor_msgs.msg import Image

from utils import inspect_rostopic_info, compute_import_path

import_path = compute_import_path('shutter_lookat', 'scripts')
sys.path.insert(1, import_path)
from fancy_virtual_camera import draw_image, compute_q, compute_rotation_axis, rotate_q

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
    # generate_target.launch.py runs for the assignment, only without RViz, which
    # the tests have no use for. MuJoCo owns the clock here -- it publishes
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
            # Not headless. mujoco_ros2_control's headless physics loop does not
            # hold the simulation to real time -- the clock advances in large,
            # irregular jumps (hundreds of simulated seconds in a few wall
            # seconds). Everything here is stamped on that clock, so under
            # headless:=true the target poses race ahead of the transforms that
            # robot_state_publisher has published and every lookup_transform at
            # the pose's own stamp fails as an extrapolation. The MuJoCo window
            # therefore has to be up for these tests, as it is when the
            # assignment is run by hand.
            'headless': 'false',
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
    fancy_virtual_camera_node = Node(
        package='shutter_lookat',
        executable='fancy_virtual_camera.py',
        name='fancy_virtual_camera_node',
        parameters=[{'use_sim_time': True}],
        # Surfaced so that a failing test shows the node's own errors
        # and warnings rather than only the assertion that failed.
        output='screen'
    )

    return (
        LaunchDescription([
            sim_launch,
            look_forward_node,
            generate_target_node,
            fancy_virtual_camera_node,
            # MuJoCo, robot_state_publisher and the chained controller
            # spawners take several seconds to come up, and each test below
            # starts its own timeout the moment ReadyToTest fires.
            TimerAction(
                period=2.0,
                actions=[ReadyToTest()]
            ),
        ]),
        {}
    )

class TestFancyVirtualCamera(unittest.TestCase):
    """
    Public tests for fancy_virtual_camera.py
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
        self.camera_info_topic = "/virtual_camera/camera_info"           # camera info topic
        self.camera_image_topic = "/virtual_camera/image_raw"            # camera info topic
        self.target_topic = "/target"                                    # target topic

        self.info_success = False
        self.image_success = False
        self.node_name = "/fancy_virtual_camera_node"             # name of the node when launched for the tests
        self.radius = 0.05   # ball radius

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
        
        self.assertTrue(success, "Failed to verify that the node {}.py "
                                 "subscribes to the {} topic".format(self.node_name, self.target_topic))

        print("Verified that the {}.py node subscribes to the {} topic".
              format(self.node_name, self.target_topic))
        sys.stdout.flush()

    def _camera_info_callback(self, msg):
        self.info_success = True
    
    def test_info_published(self):
        """
        Check that the information is being published on /virtual_camera/camera_info
        """
        self.info_success = False
        self.node.create_subscription(CameraInfo, self.camera_info_topic, self._camera_info_callback, 5)
        timeout_t = time.time() + 60  # 60 seconds in the future

        # wait patiently for a message
        while rclpy.ok() and time.time() < timeout_t and not self.info_success:
            rclpy.spin_once(self.node, timeout_sec=0.5)
        
        self.assertTrue(self.info_success, "Did not get any camera info message on {}.".format(self.camera_info_topic))
        print("Success. Got at least one camera info message through the {} topic!".format(self.camera_info_topic))
        sys.stdout.flush()

    def _image_callback(self, msg):
        self.image_success = True

    def test_image_published(self):
        """
        Check that the information is being published on /virtual_camera/camera_image
        """
        self.image_success = False
        self.node.create_subscription(Image, self.camera_image_topic, self._image_callback, 5)
        rclpy.spin_once(self.node, timeout_sec=1.0)
        timeout_t = time.time() + 60  # 60 seconds in the future
        
        # wait patiently for a message
        while rclpy.ok() and not self.image_success and time.time() < timeout_t:
            rclpy.spin_once(self.node, timeout_sec=0.5)
            time.sleep(0.5)

        self.assertTrue(self.image_success, "Did not get any image message on {}.".format(self.camera_image_topic))
        print("Success. Got at least one image message through the {} topic!".format(self.camera_image_topic))
        sys.stdout.flush()

    def test_draw_image(self):
        """
        Check the dimensions of the images output by draw_image()
        """
        x = -0.5 
        y = 0.5
        z = 1
        K = np.array([[1,1,1], [1,1,1], [1,1,1]])
        width = 256
        height = 128
        image = draw_image(x, y, z, K, width, height, radius=self.radius)
        
        self.assertIsNotNone(image, "The draw_image() function returned None instead of a valid image.")
        self.assertEqual(image.shape[0], height,
                         "The height of image was incorrect. Correct height: {}. Actual height: {}".
                         format(height, image.shape[0]))
        self.assertEqual(image.shape[1], width,
                         "The width of image was incorrect. Correct width: {}. Actual width: {}".
                         format(width, image.shape[1]))

    def test_compute_q(self):
        """
        Test compute_q function - IV-1
        """
        pt = np.array([-0.06777152, -0.14803813, 1.2686999])
        q = np.array([0., 0.04966305, 0.00579493])
        q_computed = compute_q(pt, self.radius)
        q_computed = np.reshape(q_computed, (3))

        self.assertTrue(np.allclose(q, q_computed),
                        "Computed q vector does not match expected value of q. Correct q: {}. Actual q {}".
                        format(q, q_computed))
        print("Computed q vector matched expected value.")
        sys.stdout.flush()

    def test_compute_rotation_axis(self):
        """
        Test computation of rotation axis - IV-3
        """
        pt = np.array([-0.06777152, -0.14803813, 1.2686999])
        rotation_axis = compute_rotation_axis(pt)

        self.assertEqual(len(rotation_axis), 3,
                         msg="Rotation axis should be 3-dimensional. You returned a vector of shape {}".format(
                             rotation_axis.shape))
        print("Validated that rotation axis is a 3-dimensional vector.")
        sys.stdout.flush()

    def test_rotate_q(self):
        """
        Test rotation of q - IV-4
        """
        pt = np.array([-0.06777152, -0.14803813, 1.2686999])
        q = np.array([0., 0.04966305, 0.00579493])
        rotation_axis = compute_rotation_axis(pt)
        angle = 30.

        rotated_q = rotate_q(q, rotation_axis, angle)

        self.assertEqual(len(rotated_q), 3,
                         msg="Rotation q should be 3-dimensional. You returned a vector of shape {}".format(
                             q.shape))

        print("Validated that the rotated vector is 3-dimensional.")
        sys.stdout.flush()
