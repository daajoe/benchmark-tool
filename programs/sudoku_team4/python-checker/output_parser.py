import literal


def create_separator(inner_dimension):
    """Helper function for write_output"""
    separator = ["+"] * (inner_dimension + 1)
    max_length = inner_dimension ** 2 // 10 + 1
    return ("-" * (inner_dimension * (max_length + 1) + 1)).join(separator) + "\n"


def create_line(dimension, row):
    """Helper function for write_output"""
    line = "|"
    for i in range(dimension):
        numbers = [str(number) for number in row[dimension * i: dimension * (i + 1)]]
        max_length = dimension**2 // 10 + 1
        numbers_strings = [" " * (max_length - len(number_string)) + number_string
                           for number_string in numbers]
        line += " {} |".format(" ".join(numbers_strings))

    return line


def parse_model(model, dimension):
    #print(model)
    """ parse model into sudoku puzzle matrix """
    sudoku = [[0] * dimension**2 for i in range(dimension**2)]

    # Model in Sudoku Array ueberfuehren
    for lit in model:
        #print("{} {}".format(lit, status))
        x, y, z, neg = literal.read(lit, True, dimension)
        #print("{} {} {} {}".format(x, y, z, neg))
        if neg:
            continue
        #print(z)
        if sudoku[x - 1][y - 1] != 0:
            pass
            #print("{} {} {} {} {}".format(lit, x, y, z, sudoku[x-1][y-1]))
        sudoku[x - 1][y - 1] = z

    return sudoku


def write_output(solution, dimension, total_time, solver_time):
    """Requires the model as a list of strings and the dimensions and outputs the Sudoku
    to STDOUT"""
    # Belegung ins Output Format schreiben
    # neuer Ansatz
    output = (
              # "solver time: {:.3} s \n".format(solver_time) +
              # "total time: {:.3} s \n".format(total_time) +
              "experiment: generator\n" +
              "number of tasks: 1\n" +
              "task: 1\n" +
              "puzzle size: {}x{}\n").format(dimension, dimension)

    for i in range(dimension**2):
        if i % dimension == 0:
            output += create_separator(dimension)
        output += create_line(dimension, solution[i]) + "\n"
    else:
        output += create_separator(dimension)

    print(output)
