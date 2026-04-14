"""
water_jug_core.py
=================
Water Jug Problem – Algorithm Core
Graduate Course: Heuristic Problem Solving Methods

This file contains ONLY the algorithm logic:
  - BFS (Breadth-First Search)
  - Full state space exploration and path finding
  - Console output

No visualization code is included here.
For visualization run:  python water_jug_visual.py
"""

from collections import deque
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


# ===========================================================================
#  MAIN SOLVER CLASS
# ===========================================================================

class WaterJugSolver:
    """
    Main solver class for the Water Jug Problem.

    Works with any number of jugs (2, 3, or more).
    Provides two independent solving methods:
      1. solve_bfs()             – Finds the shortest path directly via BFS
      2. solve_via_state_space() – Explores the full state space first, then finds path
    """

    # -----------------------------------------------------------------
    #  Constructor
    # -----------------------------------------------------------------
    def __init__(self, capacities, start, goal):
        """
        Parameters:
            capacities : tuple  – Maximum volume of each jug  (e.g. (8, 5, 3))
            start      : tuple  – Initial water levels         (e.g. (8, 0, 0))
            goal       : tuple  – Desired target levels        (e.g. (4, 4, 0))
        """
        self.capacities  = tuple(capacities)
        self.start       = tuple(start)
        self.goal        = tuple(goal)
        self.jug_count   = len(capacities)
        self.total_water = sum(start)

        # State space data – computed on first access (lazy initialization)
        self._all_states   = None   # set  – all reachable states
        self._transitions  = None   # dict – {state: [(neighbor, description), …]}

        # Validate inputs before doing any work
        self._validate()

    # -----------------------------------------------------------------
    #  Input Validation
    # -----------------------------------------------------------------
    def _validate(self):
        """
        Checks that capacities, start, and goal are mutually consistent.
        Raises ValueError on any violation.
        """
        if len(self.start) != self.jug_count:
            raise ValueError(
                f"Start state must have {self.jug_count} elements, "
                f"got {len(self.start)}."
            )
        if len(self.goal) != self.jug_count:
            raise ValueError(
                f"Goal state must have {self.jug_count} elements, "
                f"got {len(self.goal)}."
            )

        # Water conservation: total water must be equal in start and goal
        if sum(self.goal) != self.total_water:
            raise ValueError(
                f"Water conservation violated! "
                f"Start total: {self.total_water}, goal total: {sum(self.goal)}."
            )

        # Capacity and non-negativity checks
        for i in range(self.jug_count):
            if self.start[i] < 0 or self.goal[i] < 0:
                raise ValueError(f"Jug {i + 1}: Water amount cannot be negative.")
            if self.start[i] > self.capacities[i]:
                raise ValueError(
                    f"Jug {i + 1}: Start amount exceeds capacity ({self.capacities[i]})."
                )
            if self.goal[i] > self.capacities[i]:
                raise ValueError(
                    f"Jug {i + 1}: Goal amount exceeds capacity ({self.capacities[i]})."
                )

    # -----------------------------------------------------------------
    #  Neighbor State Generator
    # -----------------------------------------------------------------
    def _get_neighbors(self, state):
        """
        Generates all valid neighboring states reachable from a given state
        by applying the water-pouring rule.

        Rule:
            When pouring from one jug to another, either the source jug
            must become completely empty OR the destination jug must become
            completely full. Partial pours are not allowed.

        Returns:
            list of (new_state: tuple, description: str)
        """
        neighbors = []

        for i in range(self.jug_count):       # source jug index
            for j in range(self.jug_count):   # destination jug index

                if i == j:
                    continue  # Cannot pour into the same jug

                # Skip if source is empty or destination is already full
                if state[i] == 0 or state[j] >= self.capacities[j]:
                    continue

                # Amount to pour:
                #   min(water in source, available space in destination)
                amount = min(state[i], self.capacities[j] - state[j])

                # Build the new state
                new_state    = list(state)
                new_state[i] -= amount
                new_state[j] += amount
                new_state    = tuple(new_state)

                description = (
                    f"Jug {i + 1} ({self.capacities[i]}L) -> "
                    f"Jug {j + 1} ({self.capacities[j]}L): "
                    f"pour {amount}L"
                )
                neighbors.append((new_state, description))

        return neighbors

    # =================================================================
    #  METHOD 1 – BFS (Breadth-First Search)
    # =================================================================
    def solve_bfs(self):
        """
        Finds the SHORTEST path from start to goal using BFS.

        BFS processes nodes level by level (FIFO queue), which guarantees
        that the first path found reaching the goal has the minimum number
        of steps.

        Data structures:
            queue   : deque  – (current_state, path) pairs
            visited : set    – prevents revisiting states (infinite loops)

        Returns:
            list of (description, state)  – ordered solution steps
            None                          – if no solution exists
        """
        # If start already equals goal, return an empty path
        if self.start == self.goal:
            return []

        # Initialize the queue with the start state and an empty path
        queue   = deque([(self.start, [])])
        visited = {self.start}

        while queue:
            current, path = queue.popleft()   # FIFO: take the oldest node

            for neighbor, description in self._get_neighbors(current):
                if neighbor in visited:
                    continue                   # Already explored – skip

                new_path = path + [(description, neighbor)]

                # Check if we have reached the goal
                if neighbor == self.goal:
                    return new_path

                visited.add(neighbor)
                queue.append((neighbor, new_path))

        return None  # All reachable states exhausted – no solution

    # =================================================================
    #  METHOD 2 – Full State Space Exploration
    # =================================================================
    def _build_state_space(self):
        """
        Explores ALL states reachable from the start state via BFS and
        builds the complete state space graph (transition table).

        Produces two data structures:
            self._all_states   → set  – all reachable states
            self._transitions  → dict – {state: [(neighbor, description), …]}

        This corresponds to the "exploration" phase of the
        State/Solution Space Triangle discussed in the course.
        """
        # Skip if already built (lazy init guard)
        if self._all_states is not None:
            return

        self._all_states  = set()
        self._transitions = {}

        # BFS to discover every reachable state
        queue = deque([self.start])
        self._all_states.add(self.start)
        self._transitions[self.start] = []

        while queue:
            current = queue.popleft()

            for neighbor, description in self._get_neighbors(current):
                # Always record the transition (multiple edges to same node allowed)
                self._transitions[current].append((neighbor, description))

                # If this is a new state, add it to the graph
                if neighbor not in self._all_states:
                    self._all_states.add(neighbor)
                    self._transitions[neighbor] = []
                    queue.append(neighbor)

    def solve_via_state_space(self):
        """
        First builds the complete state space, then finds the shortest path
        from start to goal on that graph using BFS.

        Difference from solve_bfs():
            - The entire state space is fully explored first.
            - The path search then runs on the pre-built graph.
            - This separation mirrors the "explore → search" step order
              presented in the course material.

        Returns:
            (state_list, description_list)  – solution path
            (None, None)                    – if no solution exists
        """
        self._build_state_space()

        if self.goal not in self._all_states:
            return None, None

        if self.start == self.goal:
            return [self.start], []

        # BFS over the fully-built state space graph
        queue   = deque([(self.start, [self.start], [])])
        visited = {self.start}

        while queue:
            current, state_path, desc_path = queue.popleft()

            for neighbor, description in self._transitions.get(current, []):
                if neighbor in visited:
                    continue

                new_state_path = state_path + [neighbor]
                new_desc_path  = desc_path  + [description]

                if neighbor == self.goal:
                    return new_state_path, new_desc_path

                visited.add(neighbor)
                queue.append((neighbor, new_state_path, new_desc_path))

        return None, None

    # =================================================================
    #  CONSOLE OUTPUT
    # =================================================================
    def print_solution(self, method="bfs"):
        """
        Prints the solution to the console in a formatted, readable layout.

        Parameters:
            method : "bfs" or "state_space"
        """
        title = (
            "BFS (Breadth-First Search)"
            if method == "bfs"
            else "State Space Analysis"
        )
        line = "=" * 70

        print(f"\n{line}")
        print(f"  Water Jug Problem – {title}")
        print(f"{line}")
        print(f"  Jug Capacities : {self.capacities}")
        print(f"  Start State    : {self.start}")
        print(f"  Goal State     : {self.goal}")
        print(f"  Total Water    : {self.total_water}L")
        print(f"{line}\n")

        if method == "bfs":
            path = self.solve_bfs()
            if path is None:
                print("  [!] No solution found.\n")
                return
            if len(path) == 0:
                print("  [OK] Start state is already the goal!\n")
                return

            previous = self.start
            for i, (description, state) in enumerate(path, 1):
                print(f"  Step {i:2d}: {previous}")
                print(f"          -> {description}")
                print(f"          -> New state: {state}\n")
                previous = state

            print(f"  [OK] Goal reached in {len(path)} step(s).")

        elif method == "state_space":
            states, descriptions = self.solve_via_state_space()
            if states is None:
                print("  [!] No solution found.\n")
                return
            if len(states) == 1:
                print("  [OK] Start state is already the goal!\n")
                return

            for i in range(len(descriptions)):
                print(f"  Step {i + 1:2d}: {states[i]}")
                print(f"          -> {descriptions[i]}")
                print(f"          -> New state: {states[i + 1]}\n")

            print(f"  [OK] Goal reached in {len(descriptions)} step(s).")

        print(f"{line}\n")

    def print_state_space(self):
        """
        Prints the full state space to the console as a summary table.
        Shows the number of transitions for each state and marks
        the start (START) and goal (GOAL) states.
        """
        self._build_state_space()

        total_transitions = sum(len(v) for v in self._transitions.values())
        line = "=" * 70

        print(f"\n{line}")
        print(f"  STATE SPACE SUMMARY")
        print(f"{line}")
        print(f"  Total reachable states : {len(self._all_states)}")
        print(f"  Total transitions      : {total_transitions}")
        print(f"{line}\n")

        for state in sorted(self._all_states):
            count  = len(self._transitions.get(state, []))
            marker = ""
            if state == self.start:
                marker += "  << START"
            if state == self.goal:
                marker += "  ** GOAL"
            print(f"  {state}  ->  {count} transition(s){marker}")

        print()


# ===========================================================================
#  INPUT HELPER
# ===========================================================================

def get_input(prompt, expected_length=None):
    """
    Reads a comma-separated list of non-negative integers from the user.
    Strips parentheses and whitespace. Re-prompts on invalid input.

    Parameters:
        prompt          : str       – Message shown to the user
        expected_length : int|None  – Required number of elements (None = any)

    Returns:
        tuple of int
    """
    while True:
        try:
            raw    = input(prompt)
            raw    = raw.replace("(", "").replace(")", "").replace(" ", "")
            parts  = [int(v) for v in raw.split(",")]

            if expected_length and len(parts) != expected_length:
                print(f"  [!] Please enter exactly {expected_length} value(s).")
                continue

            if any(v < 0 for v in parts):
                print("  [!] Negative values are not allowed.")
                continue

            return tuple(parts)
        except ValueError:
            print("  [!] Invalid format. Enter integers separated by commas.")


# ===========================================================================
#  MAIN ENTRY POINT  (console output only – no visualization)
# ===========================================================================

def main():
    """
    Main entry point for the console-only mode.
    Collects user input, runs both solving methods, and prints results.

    For visualization, run:  python water_jug_visual.py
    """
    line = "=" * 70

    print(f"\n{line}")
    print("  WATER JUG PROBLEM SOLVER")
    print("  Graduate Course: Heuristic Problem Solving Methods")
    print(f"{line}\n")

    print("  Enter jug capacities separated by commas.")
    print("  The number of jugs is determined by the number of values you enter.\n")
    capacities = get_input("  Capacities (e.g. 8,5,3): ")
    jug_count  = len(capacities)
    print(f"\n  -> {jug_count} jug(s) defined: {capacities}\n")

    example_start = ",".join([str(capacities[0])] + ["0"] * (jug_count - 1))
    start = get_input(
        f"  Start state (e.g. {example_start}): ",
        expected_length=jug_count
    )
    goal = get_input(
        f"  Goal state  (e.g. 4,4,0): ",
        expected_length=jug_count
    )

    print()

    try:
        solver = WaterJugSolver(capacities, start, goal)
    except ValueError as e:
        print(f"\n  [!] Validation error: {e}")
        return

    # Method 1: BFS
    solver.print_solution(method="bfs")

    # Method 2: State space exploration then BFS
    solver.print_solution(method="state_space")

    # State space summary table
    solver.print_state_space()


if __name__ == "__main__":
    main()
