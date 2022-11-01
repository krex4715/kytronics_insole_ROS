#!/usr/bin/env python3

import rospy
import numpy as np

from std_msgs.msg import Float32MultiArray
from socket import *




class hearing_insole:
    def __init__(self):
        rospy.Subscriber("/insole_data",Float32MultiArray,self.collecting_callback)

        self.pub_phase = rospy.Publisher("AI_phase",Float32MultiArray,queue_size=10)
        self.data = np.zeros(16*20)
            

    def collecting_callback(self,data):
        self.data = np.array(data.data)
        rospy.loginfo(self.data)

    def pub_data(self):
        pub_data = Float32MultiArray()

        pub_data.data = self.data.tolist()
        # rospy.loginfo(self.data)

        self.pub_phase.publish(pub_data)


        


def main():
    rospy.init_node('insole_sub', anonymous=True)
    rate = rospy.Rate(10000)
    
    insole = hearing_insole()
    while not rospy.is_shutdown():
        insole.pub_data()
        rate.sleep()

if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass