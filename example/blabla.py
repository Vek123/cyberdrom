def get_snake_trajectory(start_point, end_point, step_x, step_y):
    cord_step_x = (end_point[0] - start_point[0]) / step_x
    cord_step_y = (end_point[1] - start_point[1]) / step_y
    curr_x = start_point[0]
    curr_y = start_point[1]
    trajectory = []
    while not [curr_x, curr_y] == end_point:
        trajectory.append([curr_x, curr_y])
        if curr_x % 2 == start_point[0] % 2:
            curr_y += cord_step_y
        else:
            curr_y -= cord_step_y
        if curr_y-1 == end_point[1]:
            curr_x += cord_step_x
            curr_y -= cord_step_y
        elif curr_y+1 == start_point[1]:
            curr_x += cord_step_x
            curr_y += cord_step_y
    trajectory.append(end_point)
    return trajectory


points = get_snake_trajectory([1, 1], [5, 8], 4, 7)
for i in points:
    print(i)

