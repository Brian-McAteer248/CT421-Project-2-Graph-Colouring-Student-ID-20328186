import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random


# Creates the adjacency matrix of a random simple graph and returns it
# (based on Erdos-Renyi random graph model)
def create_random_simple_graph(num_nodes, prob_of_creating_edge_between_two_nodes):
    # This will be a square matrix.
    # It is adjacency matrix of a simple graph (no self-edges and
    # # no more than one edge between any pair of vertices)
    adj_matrix = []

    for x in range(num_nodes):
        row = []

        # Fill in one half of matrix (including diagonals which are set to 0)
        for y in range(x + 1):
            if x == y:
                row.append(0)
            else:
                row.append(1 if random.random() < prob_of_creating_edge_between_two_nodes else 0)

        adj_matrix.append(row)

    # We have constructed half of the adjacency matrix as well as the diagonal
    # values (all 0). We will now fill in the other half of the adjacency matrix
    # and maintain matrix symmetry (this is a simple graph).
    for x in range(num_nodes):
        # For every row, iterate from one element beneath its diagonal element
        # (x + 1) down to the bottom of the respective column (num_nodes - 1)
        total_app = 0
        len_before_app = len(adj_matrix[x])
        for y in range(x + 1, num_nodes):
            # Append all the column values to the current row
            # down from the diagonal value (maintain matrix symmetry)
            # adj_matrix[y][x]: Fix the column with [x], move down the column rows as [y] is incremented
            total_app += 1
            adj_matrix[x].append(adj_matrix[y][x])

    return adj_matrix


# Returns a list of neighbours of a given node.
# Note that nodes are identified by their zero-based index e.g., for 30 nodes, node 'IDs' are 0-29
def get_node_neighbours(node, adj_matrix):
    node_row = adj_matrix[node]
    neighbours = [n for n in range(len(node_row)) if node_row[n] == 1]

    return neighbours


# Given a list of available colors, randomly assign
# colors to nodes. Returns an ordered list of colors
# corresponding to the ordering of node rows in the adjacency matrix
def rand_initialise_colors(adj_matrix, colors_list):
    colors = []

    for node in range(len(adj_matrix)):
        # Randomly assign a color from the list to a node
        color_index = random.randint(0, len(colors_list) - 1)
        colors.append(colors_list[color_index])

    return colors


# Returns the color currently associated with a particular node
def get_node_color(node, colors):
    return colors[node]


# Returns the total number of color conflicts in the graph
# specified by adj_matrix and its current coloring
def get_color_conflicts(adj_matrix, colors):
    conflicts = 0

    for node_1 in range(len(adj_matrix)):
        # We only want to iterate through the row up to but not including the diagonal
        # i.e., iterate through one half of the adjacency matrix so as not to double-count conflicts
        # e.g. if node 1 <--> node 5 and they have the same color, we want to count that conflict
        # once and not again for node 5 <--> node 1
        for node_2 in range(node_1):
            # If two nodes are adjacent, check if there is a color
            # conflict between them
            if adj_matrix[node_1][node_2] == 1:
                if get_node_color(node_1, colors) == get_node_color(node_2, colors):
                    conflicts += 1

    return conflicts


# List of all available colors that nodes will choose from. Numebr of colors
# provided from this list will be constrained as iterations progress further
all_available_colors = ["cyan", "magenta", "red", "green", "blue", "yellow", "purple", "lime", "orange", "maroon",
                        "lightsteelblue", "navy"]
num_nodes = 10
prob_of_creating_edge_between_two_nodes = 0.4

adj_matrix = create_random_simple_graph(num_nodes, prob_of_creating_edge_between_two_nodes)

# Create networkx graph object
G = nx.from_numpy_array(np.array(adj_matrix))

prob_of_node_changing_color = 0.4

# Used below for recording best achieved coloring for reporting once termination occurs
best_achieved_coloring = None

max_iterations_per_color_list = 500

for num_colors_to_include in range(len(all_available_colors), 2, -1):
    # Iteratively decrease the number of distinct colors that the agents can use for coloring
    curr_colors_list = all_available_colors[:num_colors_to_include]

    initial_random_colors = rand_initialise_colors(adj_matrix, curr_colors_list)
    initial_conflicts = get_color_conflicts(adj_matrix, initial_random_colors)

    # Create copy of the initial random coloring - this will
    # be updated as agents change their colors during the iterations
    colors = initial_random_colors.copy()

    # While there are still color conflicts in the graph
    print(f"{len(curr_colors_list)} available colors: Starting to loop through node agents")
    iteration = 0
    # Try to achieve zero conflicts. Maximum iterations is 10000.
    while get_color_conflicts(adj_matrix, colors) != 0 and iteration < max_iterations_per_color_list:
        iteration += 1
        print(f"Iteration: {iteration}, Initial conflicts: {initial_conflicts}, Current conflicts: "
              f"{get_color_conflicts(adj_matrix, colors)}, Number of colors being used: {len(set(colors))}")
        # If it conflicts with its neighbours' colorings, node will autonomously
        # decide if it will change color and, if so, which color it will pick
        for node in range(len(adj_matrix)):
            neighbours = get_node_neighbours(node, adj_matrix)
            # Use set() to remove duplicates if multiple neighbours have the same color
            unique_colors_of_neighbours = set([get_node_color(neighbour, colors) for neighbour in neighbours])

            # If the current node shares a color with any neighbour, it is in conflict
            if get_node_color(node, colors) in unique_colors_of_neighbours:
                # If true, node will decide to change its color such that it is
                # different from all its neighbours
                if random.random() < prob_of_node_changing_color:
                    # Node must choose a color from the list of available colors
                    # that is not within unique_colors_of_neighbours.
                    # It will attempt to choose colors closer to the start of
                    # colors_list. This decision strategy should constrain the
                    # total number of distinct colors used in the graph
                    old_color = colors[node]
                    for color in curr_colors_list:
                        if color not in unique_colors_of_neighbours:
                            # Node assigns itself the new color to resolve conflicts with neighbours
                            colors[node] = color
                            break

                    # The node could still have its old color here if it ran out of new colors to choose
                    # from in colors_list i.e., there were no more distinct colors left to switch
                    # to in order to resolve conflicts with neighbours. In this case, the node will simply retain its
                    # current color for this iteration.
    if get_color_conflicts(adj_matrix, colors) == 0:
        print(f"{len(curr_colors_list)} available colors: Agents achieved perfect graph coloring using "
              f"{len(set(colors))} colors.\n")
        best_achieved_coloring = colors

        plt.title(f"Solution achieved when {len(curr_colors_list)} colors available. Used {len(set(colors))} colors, "
                  f"Conflicts: {get_color_conflicts(adj_matrix, colors)}")
        nx.draw(G, node_color=colors, with_labels=True)
        plt.show()
    else:
        print(f"{len(curr_colors_list)} available colors: Agents failed to achieve perfect graph coloring.\n")
        break

# Draw graph of best achieved result
plt.title(f"Best result achieved. Used {len(set(best_achieved_coloring))} colors, Conflicts: "
          f"{get_color_conflicts(adj_matrix, best_achieved_coloring)}")
nx.draw(G, node_color=best_achieved_coloring, with_labels=True)
plt.show()
