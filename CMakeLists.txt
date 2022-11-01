cmake_minimum_required(VERSION 3.0.2)
project(insole_hear)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
)


catkin_package(
 CATKIN_DEPENDS roscpp rospy
)



include_directories(
  ${catkin_INCLUDE_DIRS}
)






