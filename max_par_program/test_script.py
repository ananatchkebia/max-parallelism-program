from max_par import Task, TaskSystem, semaphore, M1, M2, M3, M4, M5
import threading
import random
import time
from time import sleep


def main():
    # we have 6 different functions respective to 6 different tasks
    # and one additional function run_using_semaphore
    # and this last one gets previous functions as parameters
    def runT1():
        global M1
        M4 = M1

    def runT2():
        global M1, M3, M4
        M1 = M3 + M4

    def runT3():
        global M3, M4, M5
        M5 = M3 + M4

    def runT4():
        global M2, M4
        M2 = M4

    def runT5():
        global M5
        M5 = M5

    def runT6():
        global M1, M2
        M4 = M1 + M2

    def run_using_semaphore(run):
        semaphore.acquire()
        run()
        sleep(3)
        semaphore.release()

    # we have dictionary thread which matches task names to threads
    threads = {}
    threads = {
        "T1": threading.Thread(target=run_using_semaphore, args=(runT1,)),
        "T2": threading.Thread(target=run_using_semaphore, args=(runT2,)),
        "T3": threading.Thread(target=run_using_semaphore, args=(runT3,)),
        "T4": threading.Thread(target=run_using_semaphore, args=(runT4,)),
        "T5": threading.Thread(target=run_using_semaphore, args=(runT5,)),
        "T6": threading.Thread(target=run_using_semaphore, args=(runT6,))
    }

    # Define tasks
    t1 = Task("T1", read=["M1"], write=["M4"], run=runT1)
    t2 = Task("T2", read=["M3", "M4"], write=["M1"], run=runT2)
    t3 = Task("T3", read=["M3", "M4"], write=["M5"], run=runT3)
    t4 = Task("T4", read=["M4"], write=["M2"], run=runT4)
    t5 = Task("T5", read=["M5"], write=["M5"], run=runT5)
    t6 = Task("T6", read=["M1", "M2"], write=["M4"], run=runT6)

    # Define precedence constraints
    precedence = {
        "T1": [],
        "T2": ["T1"],
        "T3": ["T1"],
        "T4": ["T2", "T3"],
        "T5": ["T3"],
        "T6": ["T4", "T5"]
    }

    # Create TaskSystem instances
    s1 = TaskSystem([t1, t2, t3, t4, t5, t6], precedence)
    sMax = TaskSystem([t1, t2, t3, t4, t5, t6], precedence)
    s1.draw("Initial")
    s1.reconstruct_to_maxParallel_task_system(sMax)
    for task in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']:
        print(sMax.get_dependencies(task))
    sMax.draw("Reconstructed")

    # Check system determinism
    is_deterministic = sMax.check_system_determinism(sMax, threads, 10)
    if is_deterministic:
        print("System is deterministic.")
    else:
        print("System is non-deterministic.")

    print()
    print('RESULTS')
    print("M1", M1)
    print("M2", M2)
    print("M3", M3)
    print("M4", M4)
    print("M5", M5)
    print()

    sMax.parCost(threads)


if __name__ == "__main__":
    main()

