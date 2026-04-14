# Water Jug Problem Solver

**Graduate Course: Heuristic Problem Solving Methods**

This project is a python-based solver for the classic **Water Jug Problem**. It provides a generalized, dynamic solution that works for any number of jugs (2, 3, or N-jugs). It implements two distinct approaches to solving the problem: a standard Breadth-First Search (BFS) and a complete State Space Exploration mapped into a visual graph.

## Features

- **Dynamic Jug Support:** Define any number of capacities, start states, and target states dynamically via user input.
- **Dual Solving Strategies:**
  - **BFS (Breadth-First Search):** Finds the shortest path efficiently.
  - **State Space Exploration:** Evaluates the entire state space first, then searches for the shortest path in the resulting transition graph.
- **Visualizations:**
  - **3 Jugs:** Automatically uses an equilateral Barycentric Triangle coordinate system mapping.
  - **N Jugs:** Uses a NetworkX spring-layout directed graph.
  - Complete with dynamic highlighting of the shortest solution path.
- **Modularity:** Algorithm logic and visualizations are kept in completely separate layers.

---

## File Structure

| File | Purpose |
|------|---------|
| `water_jug_core.py` | Algorithm Core – Contains only the algorithm logic (BFS, state space exploration, and console outputs). Has absolutely **no** visualization dependencies. |
| `water_jug_visual.py` | Visualization Layer – Imports the core algorithms and renders the resulting state space graphs visually using `matplotlib` and `networkx`. |

---

## Requirements & Installation

Python 3.x is required. If you want to use the visualizer, you must install the following dependencies:

```bash
pip install matplotlib networkx
```

> **Note:** If you only need console output, you do not need to install these packages; just use the `water_jug_core.py` file.

---

## How to Run

**1. Algorithm Only Mode (Console Fallback - No Visualization):**
```bash
python water_jug_core.py
```

**2. Visualized Demo Mode:**
```bash
python water_jug_visual.py
```

### Step-by-Step Usage

Upon execution, the program will prompt you for 3 parameters:

**1. Jug capacities** – Defines how many jugs are used. Provide comma-separated values.
```text
  Capacities (e.g. 8,5,3): 8,5,3
```

**2. Start state** – Initial water amount in each jug. The length must match the number of jugs.
```text
  Start state (e.g. 8,0,0): 8,0,0
```

**3. Goal state** – The required target water distribution.
```text
  Goal state (e.g. 4,4,0): 4,4,0
```

### Input Rules

- Values must be separated by commas (e.g., `8,5,3` or `8, 5, 3`).
- Start and goal amounts cannot exceed their respective jug's capacity.
- The total amount of water in the start state must equal the total amount of water in the goal state.
- Supports any arbitrary amount of jugs (e.g., `10,7,4,2`).

---

## Example Scenarios

**Classic 3-Jug Problem:**
```text
Capacities  :  8, 5, 3
Start state :  8, 0, 0
Goal state  :  4, 4, 0
```

**Different Capacities:**
```text
Capacities  :  10, 8, 3
Start state :  10, 0, 0
Goal state  :   5, 5, 0
```

---

## Algorithm Overview

Below is the pseudo-code for the BFS algorithm utilized in this project to explore and find the solution:

```text
INPUT: Capacities, StartState, GoalState
OUTPUT: Solution Path (Steps) or Failure 

FUNCTION SolveWaterJug(Capacities, StartState, GoalState):
    Queue = EMPTY_QUEUE()
    Visited = EMPTY_SET()
    
    // Initialize data structures with start constraints
    Queue.Add( (StartState, EMPTY_PATH) )
    Visited.Add(StartState)
    
    LOOP WHILE Queue is NOT empty DO:
        CurrentState, ExploredPath = Queue.Remove()
        
        // Goal check
        IF CurrentState == GoalState THEN:
            RETURN ExploredPath
            
        // Generate neighboring achievable states
        NeighborStates = CalculateValidStates(CurrentState, Capacities)
        
        FOR EACH NewState, OperationDescription IN NeighborStates:
            IF NewState IS NOT IN Visited:
                Visited.Add(NewState)
                
                // Update path and push to queue
                NewPath = ExploredPath + OperationDescription
                Queue.Add( (NewState, NewPath) )
                
    RETURN "No Solution Found"
END
```
