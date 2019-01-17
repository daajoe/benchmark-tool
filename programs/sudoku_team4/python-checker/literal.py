def read(literal, status, inner_size):
    """ return x, y, z coords tuple from literal string """
    # literals are one based
    literal -= 1

    # extract negation
    neg = not status

    # convert 1d literal to 3d coords
    z = literal // (inner_size ** 4) + 1
    literal -= (z - 1) * (inner_size ** 4)
    y = literal // (inner_size ** 2) + 1
    x = literal % (inner_size ** 2) + 1

    return x, y, z, neg

def write(x, y, z, neg, outer_size, outer_size_squared):
    """ return literal string from x, y, z literal coords """
    # convert 3d coords to 1d literal
    literal = (z - 1) * (outer_size_squared) + (y - 1) * (outer_size) + (x - 1) + 1

    return -literal if neg else literal
