#!/usr/bin/env python3

import rospy
import yaml
import math
import actionlib

from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
from tf.transformations import quaternion_from_euler


class WaypointNavigator:
    def __init__(self):
        rospy.init_node("waypoint_navigator")

        self.mission_file = rospy.get_param(
            "~mission_file",
            "/home/hikmetunverdi/rbtg_ws/src/bookstore_service_robot/config/mission.yaml"
        )

        self.goal_timeout = rospy.get_param("~goal_timeout", 90.0)

        rospy.loginfo("Mission file okunuyor: %s", self.mission_file)

        with open(self.mission_file, "r") as file:
            self.mission = yaml.safe_load(file)

        self.locations = self.mission["locations"]

        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        rospy.loginfo("move_base action server bekleniyor...")
        self.client.wait_for_server()
        rospy.loginfo("move_base hazır.")

    def yaw_to_quaternion(self, yaw):
        q = quaternion_from_euler(0.0, 0.0, yaw)
        return q

    def create_goal(self, x, y, yaw):
        goal = MoveBaseGoal()

        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.position.z = 0.0

        q = self.yaw_to_quaternion(yaw)

        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        return goal

    def go_to_location(self, location_name):
        data = self.mission[location_name]

        x = data["goal"]["x"]
        y = data["goal"]["y"]
        yaw = data["goal"]["yaw"]

        rospy.loginfo("Yeni hedef: %s", location_name)
        rospy.loginfo("Koordinat: x=%.2f, y=%.2f, yaw=%.2f", x, y, yaw)

        goal = self.create_goal(x, y, yaw)

        self.client.send_goal(goal)

        finished = self.client.wait_for_result(rospy.Duration(self.goal_timeout))

        if not finished:
            rospy.logwarn("%s hedefi zaman aşımına uğradı. Hedef iptal ediliyor.", location_name)
            self.client.cancel_goal()
            return False

        state = self.client.get_state()

        if state == GoalStatus.SUCCEEDED:
            rospy.loginfo("%s hedefine ulaşıldı.", location_name)
            return True
        else:
            rospy.logwarn("%s hedefine ulaşılamadı. move_base state: %d", location_name, state)
            return False

    def run(self):
        rospy.loginfo("Waypoint görevi başlıyor.")

        results = {}

        for location in self.locations:
            if rospy.is_shutdown():
                break

            success = self.go_to_location(location)

            if success:
                results[location] = "SUCCESS"
            else:
                results[location] = "FAIL"

            rospy.sleep(2.0)

        rospy.loginfo("Görev tamamlandı.")
        rospy.loginfo("----- WAYPOINT RAPORU -----")

        for location, result in results.items():
            rospy.loginfo("%s: %s", location, result)


if __name__ == "__main__":
    try:
        navigator = WaypointNavigator()
        navigator.run()
    except rospy.ROSInterruptException:
        pass
