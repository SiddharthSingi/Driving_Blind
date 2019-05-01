import numpy as np
import cv2


# intersection_points is a list with pixel points of intersections on x-axis, and pixel points of intersection points on y axis
# Similarly for line_points
# Grid size is a tuple of the mapped grid (x,y)
# robot_coord, and goal_coord are pixel coordinates of the start and goal positions and are also in (x,y) format
def MakeGrid(image, intersection_thresh, line_thresh, X_points, Y_points, grid_size, kernel_size, robot_coord,
             goal_coord):
    if len(image.shape) > 2:
        print("Image must be black and white.\n")

    x_inter_pts = X_points[::2]
    y_inter_pts = Y_points[::2]

    x_line_pts = X_points[1::2]
    y_line_pts = Y_points[1::2]

    grid = np.zeros((grid_size[1], grid_size[0]))

    i = 0  # iterating in X dirn for intersections
    j = 0  # iterating in Y dirn for intersections
    for y in y_inter_pts:

        for x in x_inter_pts:

            sliced_img = image[y - kernel_size // 2:y + kernel_size // 2,
                         x - kernel_size // 2:x + kernel_size // 2]

            num_white_pix = np.count_nonzero(sliced_img)
            # print("for ", j, i, "num_pix is: ", num_white_pix)

            if num_white_pix < intersection_thresh:
                grid[j][i] = 1

            i += 2
        i=0
        j += 2

    i = 0  # iterating in X dirn for vertical lines
    j = 1  # iterating in Y dirn for vertical lines

    for y in y_line_pts:

        for x in x_inter_pts:

            sliced_img = image[y - kernel_size // 2:y + kernel_size // 2,
                         x - kernel_size // 2:x + kernel_size // 2]

            num_white_pix = np.count_nonzero(sliced_img)
            # print("for ", j, i, "num_pix is: ", num_white_pix)

            if num_white_pix < line_thresh:
                grid[j][i] = 1

            i += 2

        i=0
        j += 2

    i = 1  # iterating in X dirn for horizontal lines
    j = 0  # iterating in Y dirn for horizontal lines

    for y in y_inter_pts:

        for x in x_line_pts:

            sliced_img = image[y - kernel_size // 2:y + kernel_size // 2,
                         x - kernel_size // 2:x + kernel_size // 2]

            num_white_pix = np.count_nonzero(sliced_img)
            # print("for ", j, i, "num_pix is: ", num_white_pix)

            if num_white_pix < line_thresh:
                grid[j][i] = 1

            i += 2

        i=1
        j += 2

    # In the grid 9 blocks represent the block on the image. The 4 corners represent intersection points, the 4 edges represent lines on the image
    # however there is the middle block in the grid which represents nothing but empty space in the image. These blocks in the grid need to blocked out.

    for j in range(1, grid_size[1], 2):

        for i in range(1, grid_size[0], 2):
            grid[j][i] = 1
            #print("values are: ", j, i, "\n")

    y_robot_diff = [abs(point - robot_coord[1]) for point in Y_points]
    x_robot_diff = [abs(point - robot_coord[0]) for point in X_points]

    robot_grid = [x_robot_diff.index(min(x_robot_diff)), y_robot_diff.index(min(y_robot_diff))]

    y_goal_diff = [abs(point - goal_coord[1]) for point in Y_points]
    x_goal_diff = [abs(point - goal_coord[0]) for point in X_points]

    goal_grid = [x_goal_diff.index(min(x_goal_diff)), y_goal_diff.index(min(y_goal_diff))]

    return (grid, robot_grid, goal_grid)
