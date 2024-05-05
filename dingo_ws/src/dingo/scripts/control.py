#!/usr/bin/env python
# license removed for brevity
import rospy
from dingo_control.msg import ConCir

def talker():
    pub = rospy.Publisher('control_circuit', ConCir, queue_size=10)
    rospy.init_node('control', anonymous=False)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        control_arr = [1,1,0,0]
        
        control_string = ''.join(str(x) for x in control_arr)
        pub.publish(control_string)
        rate.sleep()
        
def main():
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
main()
