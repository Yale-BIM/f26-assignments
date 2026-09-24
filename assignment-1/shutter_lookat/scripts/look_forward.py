#!/usr/bin/env python3
"""Rotate Shutter's wrist so the camera looks forward, then exit.

Sends joint_4 to 0 through ros2_control's joint_group_controller, which takes raw
position commands on /joint_group_controller/commands. shutter_control.launch.py
brings that controller up *inactive* -- follow_trajectory_controller holds the same
position command interfaces and only one controller may claim them -- so this node
first asks /controller_manager/switch_controller to swap the two, the same way
shutter_opt_control/optimize_joints_towards_target.py does.

Once joint_4 is within tolerance of the target, the node shuts itself down. The
trajectory controller is left deactivated; anything that wants it back (MoveIt, for
instance) switches it on for itself.
"""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import numpy as np
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from controller_manager_msgs.srv import SwitchController


class LookForwardNode(Node):
    """Node that makes Shutter's wrist_1_link rotate to make the camera look forward."""

    # Order of the joints in the command array. This must match the `joints` list of
    # joint_group_controller in shutter_hardware_interface/config/position_controllers.yaml,
    # which is not necessarily the order in which /joint_states reports them.
    JOINT_ORDER = ['joint_1', 'joint_2', 'joint_3', 'joint_4']

    def __init__(self):
        super().__init__('look_forward')

        # publish rate
        publish_rate = 1  # Hz

        # parameters for the joint of interest
        self.joint_name = "joint_4"
        self.desired_joint_position = 0.0
        self.joint_reached_desired_position = False
        self.joint_command = None  # set once the first /joint_states message arrives

        # Publishers
        self.joint_pub = self.create_publisher(
            Float64MultiArray, "/joint_group_controller/commands", 5)

        # Subscribers
        self.joints_sub = self.create_subscription(JointState, "/joint_states", self.joints_callback, 5)

        # Take over the position command interfaces before publishing anything: the
        # group controller is loaded but inactive until this succeeds, so commands
        # sent beforehand are silently dropped.
        self.activate_joint_group_controller()

        # Create timer for publishing
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_joint_command)

        self.get_logger().info('Look forward node initialized')

    def activate_joint_group_controller(self):
        """Switch from follow_trajectory_controller to joint_group_controller."""
        client = self.create_client(SwitchController, "/controller_manager/switch_controller")
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("waiting for service /controller_manager/switch_controller")

        request = SwitchController.Request()
        request.activate_controllers = ["joint_group_controller"]
        request.deactivate_controllers = ["follow_trajectory_controller"]
        request.strictness = SwitchController.Request.BEST_EFFORT
        request.activate_asap = True
        request.timeout = rclpy.duration.Duration(seconds=2).to_msg()

        future = client.call_async(request)
        rclpy.spin_until_future_complete(node=self, future=future)

        if future.result() is None or not future.result().ok:
            self.get_logger().error(
                "Unable to switch to joint_group_controller; is the simulation "
                "(or shutter_hardware_interface) running?")

    def publish_joint_command(self):
        """Publish joint command if not at desired position"""
        if self.joint_command is None:
            self.get_logger().info('Waiting for /joint_states...', once=True)
            return

        if not self.joint_reached_desired_position:
            msg = Float64MultiArray()
            msg.data = list(self.joint_command)
            self.joint_pub.publish(msg)
        else:
            self.get_logger().info('Joint reached desired position, stopping node')
            self.timer.cancel()
            rclpy.shutdown()

    def joints_callback(self, msg):
        """Callback for joint state messages"""
        # /joint_states can report the joints in any order, so index them by name
        positions = dict(zip(msg.name, msg.position))
        if not all(name in positions for name in self.JOINT_ORDER):
            return

        # hold every joint where it is, and drive only the joint of interest
        self.joint_command = [positions[name] for name in self.JOINT_ORDER]
        self.joint_command[self.JOINT_ORDER.index(self.joint_name)] = self.desired_joint_position

        joint_position = positions[self.joint_name]
        self.get_logger().debug(f'joint position: {joint_position}')

        self.joint_reached_desired_position = \
            np.fabs(joint_position - self.desired_joint_position) < 1e-2
        self.get_logger().debug(f'reached? {self.joint_reached_desired_position}')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = LookForwardNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # ExternalShutdownException is how spin() reports the rclpy.shutdown() that
        # the node calls on itself once the joint has reached its target.
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
