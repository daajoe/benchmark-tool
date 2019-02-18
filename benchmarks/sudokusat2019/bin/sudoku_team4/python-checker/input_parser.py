def parse_input(path):
    """ parse a sudoku text file into a matrix and return it """
    # store sudoku as a matrix
    puzzle = list()

    with open(path, 'r') as file:
        for n, line in enumerate(file):
            # skip first 4 lines
            if n < 4:
                continue

            # extract literals and blank entries, ignore the rest
            row = list()
            cols = line.split(' ')
            for col in cols:
                if col.isalnum():
                    row.append(int(col))
                elif '_' in col:
                    row.append(0)

            if len(row) > 0:
                puzzle.append(row)

    # assert quadratic puzzle matrix
    for row in puzzle:
        if len(puzzle) != len(row):
            raise SyntaxError('malformed puzzle')

    return puzzle
