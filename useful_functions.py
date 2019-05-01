import numpy as np
import cv2
from collections import defaultdict


# ids and corners are the list taken from aruco.detectMarkers(), idstofind is a list of ids whose centre point you want to obtain. It
# should have the ids of the top left, top right, bottom right, bottom left stickers placed on the board
def FindMarkerPositions(ids, corners, idstofind):
    if not corners:
        return (None)
    else:
        # corners has a shape of (no_of_ids, 1,4,2)

        # midpoints shape is (no_ofids, 1, 2)
        midpoints = np.average(corners, axis=2)

        # search for marker ids we need index of idstofind values and take the midpoints position value of that index
        midpoint_dict = defaultdict(list)

        for i in idstofind:
            if i in ids:
                midpoint_index = list(ids).index(i)
                midpoint_dict[i] = list(midpoints[midpoint_index][0].astype(int))

        return (midpoint_dict)


## Takes the image frame, and the midpoints of the detected aruco sticker to transform the image to get an eagles eye view of the grid
## then uses the cropping pixels to remove the aruco markers from the image
def PerspectiveTransform(draw, midpoints_dict, ids_to_find, cropping_pixels):

    # ids of the marker ids in clockwise sense
    corner_ids = ids_to_find[0:4]
    robot_marker_id = ids_to_find[4]
    goal_marker_id = ids_to_find[5]

    # TL, TR, BR, BL are in clockwise order the corner coordinates that need to be used for perspective transform
    TL = corner_ids[0]
    TR = corner_ids[1]
    BR = corner_ids[2]
    BL = corner_ids[3]

    robot_posn = midpoints_dict[robot_marker_id]
    robot_posn_numpy = np.array([[robot_posn[0], robot_posn[1]]], dtype='float32')

    goal_posn = midpoints_dict[goal_marker_id]
    goal_posn_numpy = np.array([[goal_posn[0], goal_posn[1]]], dtype='float32')

    image = draw.copy()

    # cv2.circle(draw, robot_posn, 5, (255,0,0),4)

    TL = midpoints_dict[TL]
    TR = midpoints_dict[TR]
    BR = midpoints_dict[BR]
    BL = midpoints_dict[BL]

    # print(TL)

    ##Adding crcles onlly if all 4 are detected
    # cv2.circle(image, (TL[0], TL[1]), 5, (0, 0, 255), 4)
    # cv2.circle(image, (TR[0], TR[1]), 5, (0, 0, 255), 4)
    # cv2.circle(image, (BR[0], BR[1]), 5, (0, 0, 255), 4)
    # cv2.circle(image, (BL[0], BL[1]), 5, (0, 0, 255), 4)

    src = np.array([TL, TR, BR, BL], dtype='float32')

    dest = np.float32(
        [[0, 0],
         [640, 0],
         [640, 480],
         [0, 480]])

    M = cv2.getPerspectiveTransform(src, dest)
    M_numpy = np.asarray(M, dtype='float32')

    M_inv = cv2.getPerspectiveTransform(dest, src)
    M_inv_numpy = np.asarray(M_inv, dtype='float32')

    warped_robot_posn = cv2.perspectiveTransform(np.array([robot_posn_numpy]), M_numpy)
    warped_goal_posn = cv2.perspectiveTransform(np.array([goal_posn_numpy]), M_numpy)

    # print("multiplying matrix: ", M, "\n\n")
    print("warped position: ", warped_robot_posn, type(warped_robot_posn), "\n")
    print("warped_goal position: ", warped_goal_posn, type(warped_goal_posn), "\n")

    warped_img = cv2.warpPerspective(image, M, (640, 480), flags=cv2.INTER_LINEAR)

    # draw a circle on the warped robot position
    # cv2.circle(warped_img, (int(warped_robot_posn[0][0][0]),int(warped_robot_posn[0][0][1])), 10, (0,255,0), 4)

    # size of this image is 450, 580
    warped_img_cropped = warped_img[:][cropping_pixels:480 - cropping_pixels][:]
    print("shape: ", warped_img.shape)
    print(warped_img_cropped.shape)

    return (draw, warped_img_cropped, warped_robot_posn, warped_goal_posn, M_numpy, M_inv)


# Takes og thresholded image and uses the object image to blacken out the objects in the og image
def add_mask(original_image, object_threshold):
    nonzero = np.nonzero(object_threshold)
    copy = np.copy(original_image)
    nonzero_y = nonzero[0]
    nonzero_x = nonzero[1]
    for i in range(len(nonzero_y)):
        x = nonzero_x[i]
        y = nonzero_y[i]
        copy[y, x] = 0

    return (copy)


# top_view_img is a colored, cropped top view image of the map with objects.
# This functions outputs a thresholded image with the objects blackened out and the lines white
def ImageThresholding(top_view_img, map_filename):
    # cv2.imshow("input", test)

    gray = cv2.cvtColor(top_view_img, cv2.COLOR_BGR2GRAY)
    gray_mask = cv2.inRange(gray, 0,120)

    # sobel_thresh = sobel_x_thresh(top_view_img, (20,110), 3)

    hsv = cv2.cvtColor(top_view_img, cv2.COLOR_BGR2HSV)
    s_hsv = hsv[:,:,1]
    s_hsv_thresh = cv2.inRange(s_hsv, 100, 255)

    h_hsv = hsv[:,:,0]
    h_hsv_thresh = cv2.inRange(h_hsv, 0,60)

    YCrCb = cv2.cvtColor(top_view_img, cv2.COLOR_BGR2YCrCb)

    blue = top_view_img[:, :, 0]
    b_thresh = cv2.inRange(blue, 0, 140)
    green = top_view_img[:, :, 1]
    g_thresh = cv2.inRange(green, 150, 255)
    red = top_view_img[:, :, 2]
    r_thresh = cv2.inRange(red, 0, 100)

    # converting to LAB
    lab = cv2.cvtColor(top_view_img, cv2.COLOR_BGR2LAB)
    lab_b_thresh = cv2.inRange(lab[:, :, 2], 150, 255)

    lab_a_thresh = cv2.inRange(lab[:, :, 1], 130, 255)

    ##Using Median Blurring
    median = cv2.medianBlur(top_view_img, 11)
    median_thresh = cv2.inRange(median[:, :, 0], 20, 120)

    blur = cv2.GaussianBlur(top_view_img, (9, 9), 0)

    hsv_color = [30, 170, 120]
    thresh = 60

    minHSV = np.array([hsv_color[0] - thresh, hsv_color[1] - thresh, hsv_color[2] - thresh])
    maxHSV = np.array([hsv_color[0] + thresh, hsv_color[1] + thresh, hsv_color[2] + thresh])

    maskHSV = cv2.inRange(hsv, minHSV, maxHSV)

    # cv2.imshow("output", mask)
    #
    # k = cv2.waitKey(0) & 0xFF
    # # wait for ESC key to exit
    # if k == 27:
    #     cv2.destroyAllWindows()

    map_img = cv2.imread(map_filename)

    img = add_mask(map_img, s_hsv_thresh)
    img = add_mask(img, lab_b_thresh)
    img = add_mask(img, maskHSV)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return img


# Used to create sobel thresholded images in x direction
def sobel_x_thresh(image, sx_thresh=(20, 80), kernel_size=3):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=kernel_size)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=kernel_size)
    abs_sobel_x = np.absolute(sobelx)
    scaled_sobel = np.uint8(abs_sobel_x * (255 / np.max(abs_sobel_x)))
    print(scaled_sobel[120])
    sxbinary = np.zeros_like(scaled_sobel)
    sxbinary[(scaled_sobel >= sx_thresh[0]) & (scaled_sobel <= sx_thresh[1])] = 255
    print("\n\n\n")
    print(sxbinary[120])
    print(sxbinary.dtype)
    return (sxbinary)


# Used to create sobel thresholded images in y direction
def sobel_y_thresh(image, sy_thresh=(20, 80), kernel_size=3):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=kernel_size)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=kernel_size)
    abs_sobel_y = np.absolute(sobely)
    scaled_sobel = np.uint8(abs_sobel_y * (255 / np.max(abs_sobel_y)))
    sxbinary = np.zeros_like(scaled_sobel)
    sxbinary[(scaled_sobel >= sy_thresh[0]) & (scaled_sobel <= sy_thresh[1])] = 1
    return (sxbinary)


#Used to draw the marked path on the original image

# warped_posn = np.array([[[232, 455]]])
# robot_posn_numpy = np.array([[robot_posn[0], robot_posn[1]]], dtype='float32')
# cv2.perspectiveTransform(np.array([robot_posn_numpy]), M_numpy)
def Draw_on_image(positions, draw, M_numpy, M_inv):
    X_points = [35, 75, 115, 155, 198, 240, 280, 320, 360, 400, 440, 480, 523, 565, 605]
    Y_points = [20, 59, 98, 137, 176, 217, 252, 293, 330, 371, 405]

    # It is in the format (x,y)
    coordinate_points = np.zeros((11, 15, 2))

    i = 0
    j = 0
    for y in Y_points:

        for x in X_points:
            coordinate_points[j, i, :] = [x, y]
            i += 1

        i = 0
        j += 1

    # To adjust for cropping
    for j in range(len(coordinate_points)):

        for i in range(len(coordinate_points[0])):
            coordinate_points[j,i,1] += 30

    # This list contains pixel positions of path cells
    coordinate_postions = []

    for i, j in positions:
        coordinate_postions.append(np.array([int(coordinate_points[j, i][0]), int(coordinate_points[j,i][1])]))

    # unwarped_coordinate_positions = []
    # for i in range(len(coordinate_postions)):
    #     new_point = cv2.perspectiveTransform(i, M_inv_numpy)
    #     unwarped_coordinate_positions.append([new_point[0,0,0], new_point[0,0,1]])

    color = np.zeros((480,640,3), dtype='uint8')

    for i in range((len(coordinate_postions)-1)):
        pt1 = (coordinate_postions[i][0], coordinate_postions[i][1])
        pt2 = (coordinate_postions[i+1][0], coordinate_postions[i+1][1])
        cv2.line(color, pt1, pt2, (0,255,0), 9)

    rewarp = cv2.warpPerspective(color, M_inv, (640, 480))
    result = cv2.addWeighted(draw, 1, rewarp, 0.3, 0)






    return result


