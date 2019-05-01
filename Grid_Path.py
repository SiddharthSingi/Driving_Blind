import numpy as np


class Map:
    def __init__(self, initial_heading, initial_pos, grid, goal_posn):

        self.grid = grid
        self.grid[goal_posn[1], goal_posn[0]] = -1

        # closed_map is a map of closed points and the obstructions.
        # closed_data consists of two things on each point in the map, i.e point it came from and turn it took
        #  to get there
        # It is of the format array([[x_posn, y_posn], "straight"])
        #
        # Turn is different from heading in the sense that heading is how the robot is oriented when looked at
        # from the bottom it has values up, right, down, left
        # Turn on the other hand is how the robot has moved to get to that new position, acceptable turn values
        # are: left, straight, and right

        self.closed_map = np.array(self.grid)
        self.closed_data = np.zeros((self.grid.shape[0], self.grid.shape[1], 2), dtype=object)
        self.goal_posn = goal_posn

        # This map marks out any points which have been added to the open list before, so that they are not added again
        self.open_map = np.zeros_like(self.grid)

        ##This list should contain position, heading, point which it came_from, turn, cost
        self.open = []

        self.grid_heuristic = np.zeros_like(self.grid)

        # This list should contain [position, heading, (point which it came_from), turn, cost]
        self.open.append([initial_pos, initial_heading, initial_pos, "start", 0])

    def CreateHeuristic(self):
        size = self.grid_heuristic.shape
        x_init = self.goal_posn[0]
        y_init = self.goal_posn[1]

        x_diff = np.abs((np.arange(size[1]) - x_init).astype(int))
        y_diff = np.abs((np.arange(size[0]) - y_init).astype(int))

        self.grid_heuristic[y_init, :] = x_diff

        for i in range(len(x_diff)):
            self.grid_heuristic[:, i] = y_diff + self.grid_heuristic[y_init, i]

    # ALL GRID COORDINATES ARE TAKEN IN THE FORMAT [X,Y]

    def Backtrace(self, goal_turn, last_posn_data):
        turns = []
        final_positions = []

        turns.append(goal_turn)
        final_positions.append(list(self.goal_posn))

        turns.append(last_posn_data[3])
        final_positions.append(last_posn_data[0])

        came_from = last_posn_data[2]
        posn = last_posn_data[0]

        while (came_from != posn):
            final_positions.append(list(came_from))
            posn = came_from

            # Every element in self.closed_data has [came_from, turn] in the format  ([[x_posn, y_posn], "straight"])
            turn = self.closed_data[posn[1], posn[0]][1]
            turns.append(turn)

            came_from = self.closed_data[posn[1], posn[0]][0]

        # turns, and final_positions are of the same length with elements corresponding to grid points
        # starting from start position to the goal position
        return (turns[::-1], final_positions[::-1])

    def move(self):
        self.CreateHeuristic()

        def up(old_coord):
            return [old_coord[0], old_coord[1] - 1]

        def right(old_coord):
            return [old_coord[0] + 1, old_coord[1]]

        def down(old_coord):
            return [old_coord[0], old_coord[1] + 1]

        def left(old_coord):
            return [old_coord[0] - 1, old_coord[1]]

        headings = {"up": lambda x: up(x), "right": lambda x: right(x), "down": lambda x: down(x),
                    "left": lambda x: left(x)}
        turn_dict = {-1: "left", 0: "straight", 1: "right"}

        goal_reached = False
        while_counter = 1
        while not goal_reached:

            # # Testing
            # print(while_counter)
            # while_counter += 1

            self.open = sorted(self.open, key=lambda x: x[4])
            old_posn_data, self.open = self.open[0], self.open[1:]

            old_heading_index = list(headings.keys()).index(old_posn_data[1])
            old_came_from = old_posn_data[2]
            old_posn = old_posn_data[0]
            # This is the turn the robot had taken from the came_from posn to get to this new position
            old_turn = old_posn_data[3]

            new_posn_came_from = old_posn

            for i in range(-1, 2):
                new_heading = list(headings.keys())[(old_heading_index + i) % 4]
                new_turn = turn_dict[i]

                new_posn = headings[new_heading](old_posn)
                if (new_posn[0] > self.grid.shape[1] - 1 or new_posn[0] < 0 or new_posn[1] > self.grid.shape[0] - 1 or
                        new_posn[1] < 0):
                    continue

                new_cost = old_posn_data[4] + self.grid_heuristic[new_posn[1], new_posn[0]]

                # If goal has been reached
                if (self.grid[new_posn[1], new_posn[0]]) == -1:
                    print("reached somewhere good")
                    turns, positions = self.Backtrace(new_turn, old_posn_data)
                    goal_reached = True

                if ((self.closed_map[new_posn[1], new_posn[0]]) == 0 and self.open_map[new_posn[1], new_posn[0]] == 0):
                    self.open.append([new_posn, new_heading, new_posn_came_from, new_turn, new_cost])
                    self.open_map[new_posn[1], new_posn[0]] = 1

            if while_counter > 100:
                print("Something wrong")
                break

            # # Testing
            # if while_counter == 2:
            #     print(self.grid)
                # print(self.grid_heuristic)
            # print(old_posn)

            self.closed_map[old_posn[1], old_posn[0]] = 1
            self.closed_data[old_posn[1], old_posn[0]] = [old_came_from, old_turn]



        return (turns, positions)
