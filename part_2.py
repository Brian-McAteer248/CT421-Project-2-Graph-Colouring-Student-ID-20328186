import matplotlib.pyplot as plt
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


# Takes an adjacency matrix and randomly chooses num_adjencies_to_reverse pairs of nodes.
# For each selected pair:
# - If an edge exists, is it deleted.
# - If an edge doesn't exist, it is added.
def reverse_n_adjacencies(adj_matrix, num_adjencies_to_reverse):
    num_nodes = len(adj_matrix)
    max_edges = (num_nodes * (num_nodes - 1)) / 2

    adjacencies_reversed = 0

    # Outer while loop to ensure that we do add/remove num_adjencies_to_reverse edges
    while adjacencies_reversed < num_adjencies_to_reverse:
        for node_1 in range(len(adj_matrix)):
            # We only want to iterate through the row up to but not including the diagonal i.e., iterate
            # through one half of the adjacency matrix so as to preserve adjacency matrix symmetry (simple graph).
            for node_2 in range(node_1):
                # Remove existing/add new edge with probability (num_adjencies_to_reverse / num_nodes)
                if random.random() < num_adjencies_to_reverse / max_edges:
                    # 'Flip' the adjacency value i.e., remove or add an edge between node_1 and node_2
                    adj_matrix[node_1][node_2] = 1 if adj_matrix[node_1][node_2] == 0 else 0
                    adjacencies_reversed += 1

    # Return the modified adjacency matrix
    return adj_matrix


# List of all available colors that nodes will choose from. Numebr of colors
# provided from this list will be constrained as iterations progress further
all_available_colors = ["cyan", "magenta", "red", "green", "blue", "yellow", "purple", "lime", "orange", "maroon",
                        "lightsteelblue", "navy"]
num_nodes = 100
prob_of_creating_edge_between_two_nodes = 0.1

adj_matrix = create_random_simple_graph(num_nodes, prob_of_creating_edge_between_two_nodes)

prob_of_node_changing_color = 0.4

# Will use this to graph the number of distinct colors being used by agents in valid (zero conflicts) solutions going
# down (or up after perturbations) over time
best_num_colors_achieved_over_iterations = []

# Note the iterations during which the node agents have a valid graph coloring for the current graph topology
iterations_where_solution_available_for_graph = []

# Used to store the best coloring (corresponds to the lowest number of colors achieved by the
# node agents for a valid graph coloring for the current graph topology) during iterations.
current_best_valid_coloring = None

# Store the lowest coloring conflicts achieved by the node agents for the current graph topology so far
lowest_conflicts_achieved_for_current_graph = None

# Use to store lowest conflicts of coloring for current graph over iterations for the purposes of
# visualising in a line graph
lowest_conflicts_over_iterations = []

# Will use to record iterations where the graph topology was
# perturbed in order to visualise this when graphing the results
iterations_where_graph_perturbed = []

# Max times we loop over node agents in general before stopping and graphing results
max_total_iterations = 11500

# Max times we loop over node agents for a given color list
max_iterations_per_color_list = 500

# Initially provide all available colors to the node agents
num_colors_to_include = len(all_available_colors)

# How many edges to change when perturbing the graph
num_edges_to_perturb = 5

# How often to perturb the graph as the experiment runs (i.e., perturb every X iterations)
perturb_freq_in_iters = 2000

# iteration tracks ALL iterations over node agents (not just iterations over node agents for one particular colors list)
iteration = 0
while iteration < max_total_iterations:
    # Iteratively decrease (or may increase after perturbations) the number
    # of distinct colors that the agents can use for coloring
    curr_colors_list = all_available_colors[:num_colors_to_include]

    initial_random_colors = rand_initialise_colors(adj_matrix, curr_colors_list)
    initial_conflicts = get_color_conflicts(adj_matrix, initial_random_colors)

    # Create copy of the initial random coloring - this will
    # be updated as agents change their colors during the iterations
    colors = initial_random_colors.copy()

    # While there are still color conflicts in the graph
    # print(f"{len(curr_colors_list)} available colors: Starting to loop through node agents")
    curr_color_list_iteration = 0

    # Try to achieve zero conflicts.
    while get_color_conflicts(adj_matrix, colors) != 0 and curr_color_list_iteration < max_iterations_per_color_list:
        # Increment each time the node agents are looped over (tracks total iterations over time)
        iteration += 1
        # Increment each time the node agents are looped over (tracks iterations for the current color list)
        curr_color_list_iteration += 1

        print(f"(Overall) iteration: {iteration}, Initial conflicts: {initial_conflicts}, "
              f"Current conflicts: {get_color_conflicts(adj_matrix, colors)}, Number of colors being used: "
              f"{len(set(colors))}")

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
                    # current color for this iteration on the current color list.

        # Initialise lowest_conflicts_achieved_for_current_graph if this is first iteration
        if iteration == 1:
            lowest_conflicts_achieved_for_current_graph = get_color_conflicts(adj_matrix, colors)

        # Determine if lowest_conflicts_achieved_for_current_graph should be updated:

        # If conflicts of current coloring is less than lowest_conflicts_achieved_for_current_graph, set it
        # as new lowest_conflicts_achieved_for_current_graph
        if get_color_conflicts(adj_matrix, colors) < lowest_conflicts_achieved_for_current_graph:
            lowest_conflicts_achieved_for_current_graph = get_color_conflicts(adj_matrix, colors)

        # If there is a recorded current_best_valid_coloring AND it is not valid this iteration,
        # this means the graph has been perturbed. Lowest conflicts is now the conflicts of the current coloring of this
        # iteration, as this is the first iteration that the node agents have 'seen' the new topology.
        if (current_best_valid_coloring is not None and get_color_conflicts(adj_matrix, current_best_valid_coloring)
                != 0):
            lowest_conflicts_achieved_for_current_graph = get_color_conflicts(adj_matrix, colors)

        lowest_conflicts_over_iterations.append(lowest_conflicts_achieved_for_current_graph)

        # If coloring achieved after iterating over current color list has no conflicts i.e., it is valid
        if get_color_conflicts(adj_matrix, colors) == 0:
            # If a valid solution has not already been achieved
            if current_best_valid_coloring is None:
                best_num_colors_achieved_over_iterations.append(len(set(colors)))
                iterations_where_solution_available_for_graph.append(iteration)
                current_best_valid_coloring = colors
            # Otherwise, if a valid solution has already been achieved but the new solution is better
            # (node agents use a smaller list of distinct colors)
            elif len(set(colors)) < len(set(current_best_valid_coloring)):
                best_num_colors_achieved_over_iterations.append(len(set(colors)))
                iterations_where_solution_available_for_graph.append(iteration)
                current_best_valid_coloring = colors
        # If coloring achieved after iterating over current color list has conflicts i.e., it is invalid, append
        # last known best coloring IF it is still valid for the graph (graph could have been perturbed)
        elif (current_best_valid_coloring is not None and get_color_conflicts(adj_matrix, current_best_valid_coloring)
              == 0):
            best_num_colors_achieved_over_iterations.append(len(set(current_best_valid_coloring)))
            iterations_where_solution_available_for_graph.append(iteration)
        # Otherwise: latest colors aren't valid, and best known coloring no longer applies to the graph (it may
        # have been perturbed). Set current_best_valid_coloring to None i.e., node
        # agents no longer have a solution as of this iteration.
        else:
            current_best_valid_coloring = None

            # Experimental to try to break up graph into line segments!
            best_num_colors_achieved_over_iterations.append(None)
            iterations_where_solution_available_for_graph.append(None)

        # Note: If agents don't have a valid coloring (zero conflicts) for the current graph, nothing is appended to
        # best_num_colors_achieved_over_iterations. We only want to graph valid achieved numbers of colors.

        # Perturb the graph every perturb_freq_in_iters iterations over node agents
        if iteration % perturb_freq_in_iters == 0:
            adj_matrix = reverse_n_adjacencies(adj_matrix, 50)
            iterations_where_graph_perturbed.append(iteration)

    if get_color_conflicts(adj_matrix, colors) == 0:
        print(f"Achieved perfect coloring using {len(curr_colors_list)} available colors (conflicts: "
              f"{get_color_conflicts(adj_matrix, colors)}), continuing with reduced colors list\n")
        num_colors_to_include -= 1
    else:
        print(f"Failed to achieved perfect coloring using {len(curr_colors_list)} available colors (conflicts: "
              f"{get_color_conflicts(adj_matrix, colors)}) after max_iterations_per_color_list. Continuing with "
              f"increased size colors list\n")
        num_colors_to_include += 1

# Plot best zero conflict coloring solutions achieved over time, as well as when perturbations occurred
plt.xlim([0, iteration])
plt.ylim([0, len(all_available_colors) + 1])
plt.xlabel("Iterations")
plt.ylabel("Number of colors used")

plt.plot(iterations_where_solution_available_for_graph, best_num_colors_achieved_over_iterations,
         label="Number of colors used")

for iter_num in iterations_where_graph_perturbed:
    plt.axvline(x=iter_num, color="red", linestyle="--", label="Perturbation"
                if iter_num == iterations_where_graph_perturbed[0] else None)

plt.title(f"Number of colors used to achieve perfect graph coloring over iterations")
plt.legend()
plt.show()

plt.cla()

# Plot lowest conflicts achieved for current graph topology over time, as well as when perturbations occurred
plt.xlim([0, iteration])
plt.ylim([0, max(lowest_conflicts_over_iterations) + 1])
plt.xlabel("Iterations")
plt.ylabel("Number of conflicts")

x_vals = [i for i in range(1, iteration + 1)]

plt.plot(x_vals, lowest_conflicts_over_iterations, label="Number of conflicts")

for iter_num in iterations_where_graph_perturbed:
    plt.axvline(x=iter_num, color="red", linestyle="--", label="Perturbation"
                if iter_num == iterations_where_graph_perturbed[0] else None)

plt.title(f"Lowest conflicts achieved for graph in given iteration")
plt.legend()
plt.show()


