assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    naked_twins = []
    two_choices = [box for box in boxes if len(values[box]) == 2]
    for box in two_choices:
        for box2 in peers[box]:
            # enforce the order so that the pair is not taken twice
            if box < box2 and values[box] == values[box2]:
                naked_twins.append((box, box2))

    # Eliminate the naked twins as possibilities for their peers
    for box, box2 in naked_twins:
        if values[box] != values[box2]:
            # no longer twins because one of them lost one of its possible values
            continue
        elif len(values[box]) < 2:
            # both contain the same value
            return False

        twin_value = values[box]
        twin_peers = peers[box] & peers[box2]
        for peer in twin_peers:
            assign_value(values, peer, values[peer].replace(twin_value[0], '')
                                                   .replace(twin_value[1], ''))

    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

line_labels = "ABCDEFGHI"
column_labels = "123456789"

boxes = cross(line_labels, column_labels)

lines = [cross(l, column_labels) for l in line_labels]
columns = [cross(line_labels, c) for c in column_labels]
squares = [cross(l, c) for l in ('ABC', 'DEF', 'GHI') for c in ('123', '456', '789')]
diagonals = [[l+c for l, c in zip(line_labels, column_labels)],
             [l+c for l,c in zip(line_labels, reversed(column_labels))]]

units = lines + columns + squares + diagonals

peers = dict((s, set.union(*(set(unit) for unit in units if s in unit)) - {s}) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict((box, value if value != '.' else '123456789') for (box, value) in zip(boxes, grid))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    result = []
    for line in lines:
        result.append('|'.join(values[box].center(9) for box in line))
    print(('\n' + '+'.join(['-' * 9] * 9) + '\n').join(result))

def eliminate(values):
    solved = [box for box in boxes if len(values[box]) == 1]

    for s in solved:
        for peer in peers[s]:
            assign_value(values, peer, values[peer].replace(values[s], ''))
    return values

def only_choice(values):
    new_values = values.copy()

    for unit in units:
        for i in '123456789':
            choices = [box for box in unit if i in values[box]]
            if len(choices) == 1:
                assign_value(new_values, choices[0], i)

    return new_values

def n_unsolved(values):
    return len([value for value in values.values() if len(value) > 1])

def reduce_puzzle(values):
    while True:
        n_unsolved_before = n_unsolved(values)

        values = eliminate(values)
        if min(len(value) for value in values.values()) == 0:
            # some box has no possible value
            return False

        values = only_choice(values)

        values = naked_twins(values)
        if not values:
            return False

        n_unsolved_after = n_unsolved(values)

        # if there is no progress, return
        if n_unsolved_after == n_unsolved_before:
            return values

def search(values):
    # check whether constraint propagation is enough
    values = reduce_puzzle(values)
    if not values:
        return False
    if n_unsolved(values) == 0:
        return values

    # look for a box with a minimum number of possibilities
    n, box = min((len(value), box) for box, value in values.items() if len(value) > 1)

    for i in values[box]:
        new_values = values.copy()
        assign_value(new_values, box, i)
        new_values = search(new_values)
        if new_values:
            return new_values

    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
