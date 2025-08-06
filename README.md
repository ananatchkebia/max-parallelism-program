# Builder of maximal parallelism tasks' system

As we know, there are running many processes in computer, some of them run parallelly, but some processes depend on another process and one have to wait while another
will be finished.In this program I'm trying to visualise how this processes are connected to each other and trying to build system, where processes are executed maximally in
parallel. 

## Features

- I have inital direct graph, where nodes are tasks(processes), running in computer, and edges show dependendencies between tasks
- I defined memory cells and initialized them with random int values.I define two lists of memory cells for each task for reading and writing. Later,
   when I run this processes sequentially and parallelly, I call run methods for each process and they modify content of this cells
- I reconstruct initial tasks' graph for following purpose: dependencies defined initially don't take into account so called bernstein's three condition
  ( Bernstein's conditions are a set of three rules used to determine whether two program statements (or processes) can be executed in parallel without affecting the outcome.
  They are particularly useful in parallel computing and compiler optimization, and they are often expressed in terms of data dependencies between instructions )
- During program execution you can see both inital and reconstructed graphs visually
- After I reconstruct graph, I run processes sequentially and paralelly. I use topological sorting at the beginning for both of them
  ( topological sort is method which provides avoidance of cycle in task graph, as this will be reason for blockage
   and also according to dependencies provides correct order of tasks for execution )
- you can see tasks' order, while running sequentially and see which tasks are executed in paralel, while running paralelly
- I use semaphores for multithreading, while running tasks parallelly
  
## Technologies used

- OOP structure of Python programming language
- matplotlib library for drawing and showing visually processes and dependencies between them
- Bernstein's conditions
- Topological sorting
- multithreading

## How to run and how to see what this program does
you can use any IDE that supports Python programming language,
ensure you have python installed and all requered python libraries, clone this repository,  run "test_script.py" file.
At first you will see window with initial graph, you should close this window and after the second window with reconstructed graph will be popped up.
After you close this window go to CLI and see rest of information
