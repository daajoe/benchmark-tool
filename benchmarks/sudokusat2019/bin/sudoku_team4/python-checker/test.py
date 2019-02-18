import math
from output_parser import parse_model


def test_model(input, model):
    """ test the ouput of the sat solver and compare it with the input sudoku """
    outer_size = len(input)
    inner_size = int(math.sqrt(outer_size))

    # get solved puzzle matrix
    output = parse_model(model, inner_size)

    # store errors
    errors = list()

    # test number range
    for x in range(outer_size):
        for y in range(inner_size):
            val = output[x][y]
            if val <= 0 or val > outer_size:
                errors.append('Invalid number at ({x}, {y}): number = {number}'.format(
                    x=x, y=y, number=val))

    # test predefined cells
    for x in range(outer_size):
        for y in range(outer_size):
            if input[x][y] != 0 and input[x][y] != output[x][y]:
                errors.append(
                    'Deviation at ({x}, {y}): initial = {initial}, solved = {solved}'.format(
                        x=x, y=y, initial=input[x][y], solved=output[x][y])
                )

    # test row duplications
    for y in range(outer_size):
        nums = set()
        for x in range(outer_size):
            val = output[x][y]
            if val in nums:
                errors.append('Number already in row at ({x}, {y}): number = {number}'.format(
                    x=x, y=y, number=val))
            else:
                nums.add(val)

    # test column duplications
    for x in range(outer_size):
        nums = set()
        for y in range(outer_size):
            val = output[x][y]
            if val in nums:
                errors.append('Number already in column at ({x}, {y}): number = {number}'.format(
                    x=x, y=y, number=val))
            else:
                nums.add(val)

    # test subgrid duplications
    for grid_x in range(inner_size):
        for grid_y in range(inner_size):
            nums = set()
            for x in range(grid_x * inner_size, (grid_x + 1) * inner_size):
                for y in range(grid_y * inner_size, (grid_y + 1) * inner_size):
                    val = output[x][y]
                    if val in nums:
                        errors.append(
                            'Number already in grid at ({x}, {y}): number = {number}'.format(
                                x=x, y=y, number=val)
                        )
                    else:
                        nums.add(val)

    # print errors
    if len(errors) > 0:
        for error in errors:
            print(error)
    else:
        print('No errors found in output sudoku puzzle.')
