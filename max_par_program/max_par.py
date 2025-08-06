import copy
import queue
import networkx as nx
import matplotlib.pyplot as plt
import threading
import time
from time import sleep
import random
import timeit

# Define semaphore to limit concurrent access
semaphore = threading.Semaphore(5)

# Define global variables M1, M2, M3, M4, M5 and give them random values
M1 = random.randint(1, 5)
M2 = random.randint(1, 5)
M3 = random.randint(1, 5)
M4 = random.randint(1, 5)
M5 = random.randint(1, 5)


# Task class represents a single task
# field dependencies contains task objects which should have been executed before current task execution
# read and write lists contain memory cells,for reading and writing respectively
class Task:
    def __init__(self, name="", dependencies=[], read=[], write=[], run=None):
        self.name = name
        self.dependencies = dependencies
        self.read = read
        self.write = write
        self.run = run


# TaskGraph class manages tasks and their dependencies
# It has one field which is dictionary data structure and
# contains task names(string) and their correspondent list of dependencies
class TaskGraph:
    def __init__(self):
        self.tasks = {}

    # Method to add a task to the task graph
    def add_task(self, task):
        self.tasks[task.name] = task

    # Method to check if there's a path between two tasks(from x to y)
    # it uses queue data structure and does DFS
    # finally it returns boolean value,True if path exists,otherwise- False
    def isReachable(self, x, y):
        if (x == y): return True
        visited = {}
        for key in self.tasks:
            visited[key] = False
        q = queue.Queue()
        visited[x] = True
        q.put(x)
        while not q.empty():
            x = q.get()
            for k in self.tasks[x].dependencies:
                if (k == y): return True
                if (visited[k] == False):
                    q.put(k)
                    visited[k] = True
        return False


# ValidationSystem class validates input tasks and their dependencies
# It provides avoidance of duplicate task names,duplication of tasks in the same dependencies list
# and avoids reference to nonexisted tasks
class ValidationSystem:
    def validate_input(tasks, precedence):
        task_names = set()
        task_dependents = set()
        for task in tasks:
            if task.name in task_names:
                print(f"Duplicate task name '{task.name}' found.")
                return False
            task_names.add(task.name)
            if (task.name in precedence):
                for dep_task_name in precedence[task.name]:
                    if dep_task_name in task_dependents:
                        print(f"Error: Duplicate task dependent '{dep_task_name}' found.")
                        exit()
                    task_dependents.add(dep_task_name)
                    task_dependents.clear()
            else:
                print(f"Error: Dependences for such task name {task.name} does not exist.");
                return False

        for task_name, dependencies in precedence.items():
            # Check if task name exists in tasks list
            if task_name not in task_names:
                print(f"Error: Task name '{task_name}' not found in the list of tasks.")
                return False

            # Check if dependencies exist in tasks list
            for dep_task_name in dependencies:
                if dep_task_name not in task_names:
                    print(f"Error: Dependency '{dep_task_name}' of task '{task_name}' not found in the list of tasks.")
                    return False

        return True


# TaskScheduler class provides methods to schedule and execute tasks
# This class doesn't have constructor as we never make TaskScheduler class's object as it is additional class,
# all methods are called from TaskSystem class methods,so all method here are static methods to provide their
# calling with class name,without instantiating this class
class TaskScheduler:
    # At the beginning sequential execution method calls topological sort method to get tasks list
    # with correct order to execute
    # sequencial execution method only needs to iterate on this list and call run function for each of them
    # Its notable that this function as well as execution_in_parallel starts and ends with variables
    # which keeps current times,and function returns subtraction of them
    @staticmethod
    def execute_sequentially(task_graph):
        # Sort tasks based on precedence constraints
        tasks = TaskScheduler.topological_sort(task_graph)
        print("Running tasks sequentially:")
        total_time = 0
        for task in tasks:
            print("TASK RUNNING", task.name)
            start = time.perf_counter()
            task.run()
            end = time.perf_counter()
            total_time += end - start
        return total_time

    # parallel execution function groups tasks which are able to execute parallely in parallel_tasks list
    # and after execution these tasks adds them in tasks_completed list to avoid their execution in second time
    @staticmethod
    def execute_in_parallel(task_graph, threads):
        tasks = TaskScheduler.topological_sort(task_graph)
        tasks_completed = []
        parallel_tasks = []
        while len(tasks_completed) < len(tasks):
            for task in tasks:
                if task.name not in tasks_completed and (len(task.dependencies) == 0 or all(
                        task_dep in tasks_completed for task_dep in task.dependencies)):
                    parallel_tasks.append(task.name)
            print("parallel_tasks ", parallel_tasks)
            total_time = 0
            while len(parallel_tasks) != 0:
                for parallel_task in parallel_tasks:
                    start = time.perf_counter()
                    if not threads[parallel_task].is_alive():
                        threads[parallel_task].start()
                    end = time.perf_counter()
                    total_time += end - start
                    parallel_tasks.remove(parallel_task)
                    tasks_completed.append(parallel_task)
        return total_time

    # topological sort method is helper method which provides avoidance of cycle in task graph
    # (as this will be reason for blockage )
    # and also according to dependencies provides correct order of tasks for execution
    @staticmethod
    def topological_sort(task_graph):
        in_degree = {task_id: 0 for task_id in task_graph.tasks}
        for task in task_graph.tasks.values():
            for dep_id in task.dependencies:
                in_degree[dep_id] += 1
        queue = [task_id for task_id, indeg in in_degree.items() if indeg == 0]
        result = []
        while queue:
            task_id = queue.pop(0)
            result.append(task_graph.tasks[task_id])
            for dep_id in task_graph.tasks[task_id].dependencies:
                in_degree[dep_id] -= 1
                if in_degree[dep_id] == 0:
                    queue.append(dep_id)
        if len(result) != len(task_graph.tasks):
            print("Graph contains a cycle")
            exit()
        return list(reversed(result))

    # following method instantiates TaskGraph class
    # after tasks list and precedence dictionary will pass validations tasks dictionary will be complated
    # if validation process will have problems program will exit
    @staticmethod
    def build_task_system(tasks, precedence):
        task_graph = TaskGraph()
        input_is_valid = ValidationSystem.validate_input(tasks, precedence)
        if input_is_valid:
            for task in tasks:
                task.dependencies = precedence[task.name]
                task_graph.add_task(task)
            return task_graph
        else:
            exit()

    # We should reconstruct initial task system to real maximal parallel system and following method does this
    # At the beginning,it gets two taskSystem objects as arguments and both of them contain same data
    # we should maintain task_graph's data and modify max_parallel_system_graph's data according to Bernstein's conditions
    @staticmethod
    def reconstruct(task_graph, max_parallel_system_graph):
        task_graph_copy = copy.deepcopy(task_graph)
        # bernstein's conditions check is valid for such (x,y) task pairs where y is reachable from x
        # here we use taskGraph class's method isReachable
        # We check bernstein's three condition and according to their results remove or add edges
        for task_x_name in task_graph_copy.tasks:
            for task_y_name in task_graph_copy.tasks:
                if (task_x_name == task_y_name):
                    continue

                if (task_graph_copy.isReachable(task_x_name, task_y_name)):
                    condition1 = True
                    condition2 = True
                    condition3 = True
                    for task_read_k in task_graph_copy.tasks[task_x_name].read:
                        for task_write_l in task_graph_copy.tasks[task_y_name].write:
                            if (task_read_k == task_write_l):
                                condition1 = False
                    for task_read_k in task_graph_copy.tasks[task_y_name].read:
                        for task_write_l in task_graph_copy.tasks[task_x_name].write:
                            if (task_read_k == task_write_l):
                                condition2 = False
                    for task_write_k in task_graph_copy.tasks[task_x_name].write:
                        for task_write_l in task_graph_copy.tasks[task_y_name].write:
                            if (task_write_k == task_write_l):
                                condition3 = False
                    all_conditions_together = condition1 and condition2 and condition3
                    exists = False
                    for task_dep_n in task_graph_copy.tasks[task_x_name].dependencies:
                        if (task_dep_n == task_y_name):
                            exists = True
                    if (not all_conditions_together and not exists):
                        max_parallel_system_graph.tasks[task_x_name].dependencies.append(task_y_name)
                    if (all_conditions_together and exists):
                        max_parallel_system_graph.tasks[task_x_name].dependencies.remove(task_y_name)

        # finally we remove redundant edges
        # for (x,y) edge if in graph exists another path from x to y we remove (x,y) edge
        for task_name in max_parallel_system_graph.tasks:
            for dep in max_parallel_system_graph.tasks[task_name].dependencies:
                q = queue.Queue()
                q.put(task_name)
                depth = 1
                found = False
                while not q.empty():
                    task_x_name = q.get()
                    for task_dep_k in max_parallel_system_graph.tasks[task_x_name].dependencies:
                        if (dep == task_dep_k and depth != 1):
                            found = True
                            max_parallel_system_graph.tasks[task_name].dependencies.remove(dep)
                        q.put(task_dep_k)
                    if (found): break
                    depth += 1

    # parCost method prints times for both type of executions
    @staticmethod
    def parCost(task_graph, threads):
        #exec_time_seq = TaskScheduler.execute_sequentially(task_graph)
        execution_time_sequentially = timeit.timeit("TaskScheduler.execute_sequentially", globals=globals(), number=1000)
        execution_time_parallel = timeit.timeit("TaskScheduler.execute_in_parallel", globals=globals(), number=1000)

        print("exec_time_seq_method", execution_time_sequentially)
        print("running_time_seq_tasks", TaskScheduler.execute_sequentially(task_graph))
        print("exec_time_parallel_method", execution_time_parallel)
        print("running_time_parallel_tasks", TaskScheduler.execute_in_parallel(task_graph, threads))

    # this method is for graph drawing
    @staticmethod
    def display_precedence_graph(task_graph, name):
        G = nx.DiGraph()
        for task_id, task in task_graph.tasks.items():
            if (len(task.dependencies) == 0):
                G.add_node(task_id)
            for dep_id in task.dependencies:
                G.add_edge(dep_id, task_id)
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')
        plt.title(name + " Graph")
        plt.axis('off')
        plt.show()


# TaskSystem class represents a collection of tasks with precedence constraints
# and it contains different functionalities of this system
class TaskSystem:
    def __init__(self, tasks, precedence):
        self.task_graph = TaskScheduler.build_task_system(tasks, precedence)

    def get_dependencies(self, task_name):
        if task_name in self.task_graph.tasks:
            return self.task_graph.tasks[task_name].dependencies
        else:
            print(f"Error: Task name {task_name} does not exist.");

    def reconstruct_to_maxParallel_task_system(self, max_parallel_system):
        TaskScheduler.reconstruct(self.task_graph, max_parallel_system.task_graph)

    def run_seq(self):
        TaskScheduler.execute_sequentially(self.task_graph)

    def run(self, threads):
        TaskScheduler.execute_in_parallel(self.task_graph, threads)

    def draw(self, name):
        TaskScheduler.display_precedence_graph(self.task_graph, name)

    def parCost(self, threads):
        TaskScheduler.parCost(self.task_graph, threads)

    def check_system_determinism(self, task_system, threads, num_trials):
        '''
        Check system determinism by running the task system multiple times and verifying if the execution order
        (and the final result) remains the same.
        '''

        print()
        print('Initial values: ')
        print("M1", M1)
        print("M2", M2)
        print("M3", M3)
        print("M4", M4)
        print("M5", M5)
        print()

        previous_order = []
        for _ in range(num_trials):
            tasks = TaskScheduler.topological_sort(task_system.task_graph)
            print("Test run ", _ + 1)
            execution_order = []
            # Run the task system in parallel
            task_system.run(threads)

            # Get the execution order of tasks
            for task in tasks:
                # print(task.name)
                execution_order.append(task.name)
            # Check if the execution order remains the same for each trial
            if len(previous_order) > 0 and execution_order != previous_order:
                return False
            previous_order = copy.deepcopy(execution_order)

        return True
