# Driving_Blind
This project aims to use computer vision to plan the path of AGVs in a closed environment using ArUco stickers and camera images.

Line following robots, AGVs, or other mobile robots traditionally employ multiple on board sensors and computing graphics cards to map the environment around them and plan their path. This project is a small attempt to map the entire area using an image mounted at a height which can then be used to send only movement instructions to a robot without having to use expensive on board sensors.

## Environment Used:
1) We have printed a grid map on a flex banner material consisting of a 5x7 grid.
(Put image here)

2) We built a line following robot which can detect interssections and follow a path sent to it(put image here)

1) We have placed random objects at various points on the map

1) 6 ArUco stickers have been used to detect the four corners on the map, and the position of the robot and the goal position.


## Structure
The entire code consists of the following steps:

* Continuously take images from the camera till all 6 ArUco stickers are identified.
* Use the four corner stickers to create a Perspective transformed top view image of the enitre area.
* Use different color spaces to create a binary image of only the objects creating an obstruction on the map
* Use the original map and the obstructions detected to create a virtual array of start, goal and obstructions.
* Use A* path planning to detect the optimal route to take to reach the goal position
* Use the optimal route to color the original route with the shortest path.
