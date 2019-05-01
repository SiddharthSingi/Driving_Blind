import numpy as np
import cv2
import cv2.aruco as aruco
from useful_functions import FindMarkerPositions
from useful_functions import PerspectiveTransform
from useful_functions import ImageThresholding, Draw_on_image
import time
from Grid import MakeGrid
from Grid_Path import Map

cap = cv2.VideoCapture(0)
correct_frame = 0
X_points = [35, 75, 115, 155, 198, 240, 280, 320, 360, 400, 440, 480, 523, 565, 605]
Y_points = [20, 59, 98, 137, 176, 217, 252, 293, 330, 405]

while (True):

    # Capture frame-by-frame
    ret, frame = cap.read()
    # print(frame.shape) #480x640

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Our operations on the frame come here
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()

    # print(parameters)

    '''    detectMarkers(...)
        detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
        mgPoints]]]]) -> corners, ids, rejectedImgPoints
        '''
    # lists of ids and the corners beloning to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    draw = aruco.drawDetectedMarkers(frame, corners)

    # print("draw shape: ", draw.shape)

    # idstofind has the ids of the four corner marker ids in clockwise and then the robot marker id and then the goal marker id
    idstofind = [0, 1, 4, 5, 2, 3]

    # midpoints eg: [[7, array([437. , 245.5], dtype=float32)], [8, array([343., 162.], dtype=float32)]] .
    # The first number is the marker id and the second array is the position of that id
    midpoints_found = FindMarkerPositions(ids, corners, idstofind)

    # print(midpoints_found)

    # Adding Text
    # if midpoints_found is not None:
    #     for id, midpoint in midpoints_found.items():
    #         cv2.putText(draw, ("id no: " + str(id)), (midpoint[0], midpoint[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 2)

    # ids of the marker ids in clockwise sense
    cornerIds = idstofind[0:4]

    robot_marker_id = idstofind[4]

    if midpoints_found is not None:
        if (len(midpoints_found) == 6):
            draw, cropped_warped_img, warped_robot_coord, warped_goal_coord, M_numpy, M_inv = PerspectiveTransform(draw,
                                                                                                   midpoints_found,
                                                                                                   idstofind, 30)

            print(cropped_warped_img.shape)
            thresh = ImageThresholding(cropped_warped_img, "Map_cheat_ultimate.jpg")

            grid_size = [15, 11]
            intersection_thresh = 450
            line_thresh = 250
            kernel_size = 40

            # -30 because we have cropped the image using cropping pixels in PerspectiveTransform and these
            #  pixel positions are of the previous non cropped image
            robot_coord = [warped_robot_coord[0,0,0], warped_robot_coord[0,0,1]-30]
            goal_coord = [warped_goal_coord[0,0,0], warped_goal_coord[0,0,1]-30]

            grid, robot_grid, goal_grid = MakeGrid(thresh, intersection_thresh, line_thresh, X_points, Y_points, grid_size, kernel_size, robot_coord,
                     goal_coord)

            print(grid)
            print(robot_grid)
            print(goal_grid)

            # TODO: set up initial_heading
            initial_heading = "up"
            robu = Map(initial_heading, robot_grid, grid, goal_grid)
            turns, positions = robu.move()



            turns_to_arduino = []
            for dirn in turns[1::2]:
                if (dirn=="right"):
                    turns_to_arduino.append("R")
                if (dirn=="left"):
                    turns_to_arduino.append("L")
                if (dirn=="straight"):
                    turns_to_arduino.append("S")


            draw_image = Draw_on_image(positions, draw, M_numpy, M_inv)
            print(type(draw_image))
            print(draw_image.shape)
            print(np.count_nonzero(draw_image))
            print("\n" + "Turns and positions are: ", turns_to_arduino, "\n", positions)
            cv2.imwrite("initial_image.jpg", draw)
            cv2.imshow("result", draw_image)
            cv2.imwrite("final_output.jpg", draw_image)



            # #
            # # # to save the images
            # # cv2.imwrite((str(correct_frame) + ".jpg"), cropped_warped_img)
            #
            # cv2.imshow('frame', cropped_warped_img)
            # # cv2.imshow('cropped_top', cropped_warped_img)
            # # cv2.destroyAllWindows()
            # cv2.imwrite('transformed' + (str(correct_frame) + '.jpg'), cropped_warped_img)
            # # cv2.imshow('thresh', thresh)
            # correct_frame += 1




        else:
            # Display the resulting frame
            cv2.imshow('frame', draw)

    else:
        pass
        # Display the resulting frame
        cv2.imshow('frame', draw)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
