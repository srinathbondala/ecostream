from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import numpy as np

# Import Distance Matrix
df_distance = pd.read_excel('df_distance_matrix.xlsx', index_col=0, engine='openpyxl')


# Transform to Numpy Array
distance_matrix = df_distance.to_numpy()

# Create dictionary with data
data = {}
data['distance_matrix'] = distance_matrix
print("{:,} destinations".format(len(data['distance_matrix'][0]) - 1))

# Time windows for each location (in minutes)
time_windows = [(0, 0),  # Depot
                (75, 85), (75, 85), (60, 70), (45, 55),  # 1-4
                (0, 30), (10, 20), (0, 10), (75, 85),  # 5-8
                (85, 95), (5, 15), (15, 25), (10, 20),  # 9-12
                (45, 55), (30, 40), (75, 85), (85, 95)]  # 13-16
data['time_windows'] = time_windows

# Orders quantity (Boxes)
data['demands'] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]

# Vehicles Capacities (Boxes)
data['vehicle_capacities'] = [15, 15, 15, 15]

# Number of vehicles
data['num_vehicles'] = 4
# Location of the depot
data['depot'] = 0

def distance_callback(from_index, to_index):
    """Returns the distance between the two nodes."""
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['distance_matrix'][from_node][to_node]

def demand_callback(from_index):
    """Returns the demand of the node."""
    from_node = manager.IndexToNode(from_index)
    return data['demands'][from_node]

def time_callback(from_index, to_index):
    """Returns the travel time between the two nodes."""
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

def time_windows_callback(from_index):
    """Returns the time windows of the node."""
    from_node = manager.IndexToNode(from_index)
    return data['time_windows'][from_node]

# Create the routing index manager
manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                        data['num_vehicles'], data['depot'])

# Create Routing Model
routing = pywrapcp.RoutingModel(manager)

# Create and register distance callback
transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Add Capacity constraint
demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(demand_callback_index,
                                        0,  # null capacity slack
                                        data['vehicle_capacities'],  # vehicle maximum capacities
                                        True,  # start cumul to zero
                                        'Capacity')

# Add Time Window constraint
time_callback_index = routing.RegisterTransitCallback(time_callback)
routing.AddDimensionWithVehicleTransits(
    time_callback_index,
    30,  # allow waiting time
    300,  # maximum time per vehicle
    False,  # don't force start cumul to zero since we are not using time windows at the depot
    'Time')

# Add Time Window constraints for each location
time_windows_callback_index = routing.RegisterTransitCallback(time_windows_callback)
routing.AddDimensionWithVehicleTransits(
    time_windows_callback_index,
    0,  # no waiting time
    300,  # maximum time per vehicle
    True,  # force start cumul to zero as we use time windows at each location
    'Time_Window')

# Set first solution heuristic
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

# Solve the problem
solution = routing.SolveWithParameters(search_parameters)

# Output solution
if solution:
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for driver {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Parcels({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Parcels({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {} (m)\n'.format(route_distance)
        plan_output += 'Parcels Delivered: {} (parcels)\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {:,} (m)'.format(total_distance))
    print('Parcels Delivered: {:,}/{:,}'.format(total_load, sum(data['demands'])))
else:
    print('No Solution')
