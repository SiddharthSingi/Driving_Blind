# Driving_Blind
This project aims to use computer vision to plan the path of AGVs in a closed environment using ArUco stickers and camera images.

Line following robots, AGVs, or other mobile robots traditionally employ multiple on board sensors and computing graphics cards to map the environment around them and plan their path. This project is a small attempt to map the entire area using an image mounted at a height which can then be used to send only movement instructions to a robot without having to use expensive on board sensors.

## Environment Used:
1) We have printed a grid map on a flex banner material consisting of a 5x7 grid.
![initial_image](https://user-images.githubusercontent.com/26694585/57016662-ff609980-6c38-11e9-89bd-f2f9b98c51a3.jpg)

2) We built a line following robot which can detect interssections and follow a path sent to it(put image here)

1) We have placed random objects at various points on the map

1) 6 ArUco stickers have been used to detect the four corners on the map, and the position of the robot and the goal position.


## Structure
The entire code consists of the following steps:

* Continuously take images from the camera till all 6 ArUco stickers are identified.
* Use the four corner stickers to create a Perspective transformed top view image of the enitre area.
![transformed4](https://user-images.githubusercontent.com/26694585/57016687-18694a80-6c39-11e9-9bcc-f2f29611d380.jpg)

* Use different color spaces to create a binary image of only the objects creating an obstruction on the map
![Lab_b_thresh](https://user-images.githubusercontent.com/26694585/57016671-0a1b2e80-6c39-11e9-9f59-21ad498b0d34.jpg)


* Use the original map and the obstructions detected to create a virtual array of start, goal and obstructions.
![final_obj_thresh](https://user-images.githubusercontent.com/26694585/57016674-10110f80-6c39-11e9-8a57-e6c3125e5943.jpg)

* Use A* path planning to detect the optimal route to take to reach the goal position

* Use the optimal route to color the original route with the shortest path.
![final_output](https://user-images.githubusercontent.com/26694585/57016665-01c2f380-6c39-11e9-8f7f-6bb29672fa47.jpg)









