#!/usr/bin/env python3

import rospy
import cv2

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


class QRReader:
    def __init__(self):
        rospy.init_node("qr_reader")

        self.bridge = CvBridge()
        self.detector = cv2.QRCodeDetector()

        self.image_topic = rospy.get_param("~image_topic", "/camera/rgb/image_raw")

        self.pub = rospy.Publisher("/qr_code_data", String, queue_size=10)

        self.last_qr = ""
        self.last_publish_time = rospy.Time.now()

        rospy.Subscriber(self.image_topic, Image, self.image_callback)

        rospy.loginfo("QR Reader baslatildi.")
        rospy.loginfo("Kamera topic: %s", self.image_topic)
        rospy.loginfo("QR sonucu /qr_code_data topicine yayinlanacak.")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            rospy.logwarn("Goruntu cv2 formatina cevrilemedi: %s", str(e))
            return

        qr_data, points, _ = self.detector.detectAndDecode(frame)

        if qr_data:
            now = rospy.Time.now()

            if qr_data != self.last_qr or (now - self.last_publish_time).to_sec() > 1.0:
                self.last_qr = qr_data
                self.last_publish_time = now

                rospy.loginfo("QR okundu: %s", qr_data)
                self.pub.publish(qr_data)

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    reader = QRReader()
    reader.run()
