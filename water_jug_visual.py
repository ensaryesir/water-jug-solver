"""
water_jug_visual.py
====================
Water Jug Problem – Visualization Layer
Graduate Course: Heuristic Problem Solving Methods

This file imports the algorithm core from water_jug_core.py and adds
visual output. All algorithm logic lives in the core module.

Dependencies:
    pip install matplotlib networkx

Usage:
    python water_jug_visual.py
"""

import math
import sys

from water_jug_core import WaterJugSolver, get_input

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Visualization libraries (optional – program still runs without them)
# ---------------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import networkx as nx
    VISUAL_AVAILABLE = True
except ImportError:
    VISUAL_AVAILABLE = False


# ===========================================================================
#  VISUALIZER CLASS
# ===========================================================================

class WaterJugVisualizer:
    """
    Takes a WaterJugSolver instance and draws the full state space graph
    along with the highlighted solution path.

    3 jugs  ->  Barycentric (triangle) coordinate system
    N jugs  ->  NetworkX spring-layout graph
    """

    def __init__(self, solver: WaterJugSolver):
        """
        Parameters:
            solver : WaterJugSolver  – A solver that has already run its algorithms
        """
        self.solver = solver

        # Ensure the state space has been built on the solver
        self.solver._build_state_space()

        # Build a NetworkX directed graph for drawing
        self._nx_graph = None
        if VISUAL_AVAILABLE:
            self._nx_graph = nx.DiGraph()
            for state in self.solver._all_states:
                self._nx_graph.add_node(state)
            for state, transitions in self.solver._transitions.items():
                for neighbor, _ in transitions:
                    self._nx_graph.add_edge(state, neighbor)

    # -----------------------------------------------------------------
    #  Barycentric Coordinate Conversion (3-jug only)
    # -----------------------------------------------------------------
    def _barycentric(self, state):
        """
        Maps a 3-jug state (a, b, c) to Cartesian (x, y) coordinates
        inside an equilateral triangle.

        Corner mapping:
            Jug 1  ->  bottom-left  (0,   0)
            Jug 2  ->  bottom-right (1,   0)
            Jug 3  ->  top-center   (0.5, sqrt(3)/2)

        Each component is normalized by the total water volume.
        """
        total = self.solver.total_water if self.solver.total_water > 0 else 1
        _a, b, c = state
        nb = b / total
        nc = c / total
        x  = nb + 0.5 * nc
        y  = nc * math.sqrt(3) / 2
        return x, y

    # -----------------------------------------------------------------
    #  Main draw – dispatch by jug count
    # -----------------------------------------------------------------
    def draw(self, solution_path=None):
        """
        Dispatches to the appropriate drawing method based on jug count.

        Parameters:
            solution_path : list of tuple  – States along the solution path (optional)
        """
        if not VISUAL_AVAILABLE:
            print("\n  [!] matplotlib and/or networkx are not installed.")
            print("      Install with:  pip install matplotlib networkx")
            return

        if self.solver.jug_count == 3:
            self._draw_triangle(solution_path)
        else:
            self._draw_graph(solution_path)

    # -----------------------------------------------------------------
    #  3-Jug – Barycentric Triangle Visualization
    # -----------------------------------------------------------------
    def _draw_triangle(self, solution_path=None):
        """
        Draws the entire state space using barycentric triangle coordinates.
        Solution path edges are drawn in thick red; all other edges in thin grey.
        """
        solver = self.solver
        fig, ax = plt.subplots(figsize=(14, 12))
        ax.set_aspect("equal")

        # ---------- Triangle frame ----------
        triangle = plt.Polygon(
            [(0, 0), (1, 0), (0.5, math.sqrt(3) / 2)],
            fill=False, edgecolor="#555555", linewidth=2, linestyle="--"
        )
        ax.add_patch(triangle)

        # Corner labels
        ofs = 0.06
        ax.annotate(
            f"Jug 1\n({solver.capacities[0]}L)",
            xy=(-ofs, -ofs), fontsize=11, ha="center",
            fontweight="bold", color="#1565C0"
        )
        ax.annotate(
            f"Jug 2\n({solver.capacities[1]}L)",
            xy=(1 + ofs, -ofs), fontsize=11, ha="center",
            fontweight="bold", color="#2E7D32"
        )
        ax.annotate(
            f"Jug 3\n({solver.capacities[2]}L)",
            xy=(0.5, math.sqrt(3) / 2 + ofs), fontsize=11, ha="center",
            fontweight="bold", color="#E65100"
        )

        # ---------- Collect solution edges and nodes ----------
        solution_edges = set()
        solution_nodes = set()
        if solution_path:
            solution_nodes = set(solution_path)
            for k in range(len(solution_path) - 1):
                solution_edges.add((solution_path[k], solution_path[k + 1]))

        # ---------- All edges (grey, thin) ----------
        for state, transitions in solver._transitions.items():
            x1, y1 = self._barycentric(state)
            for neighbor, _ in transitions:
                if (state, neighbor) in solution_edges:
                    continue   # Will be drawn separately
                x2, y2 = self._barycentric(neighbor)
                ax.annotate(
                    "", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="->", color="#CCCCCC", lw=0.5, alpha=0.35
                    )
                )

        # ---------- Solution path edges (red, thick) ----------
        if solution_path:
            for k in range(len(solution_path) - 1):
                x1, y1 = self._barycentric(solution_path[k])
                x2, y2 = self._barycentric(solution_path[k + 1])
                ax.annotate(
                    "", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="-|>", color="#D32F2F", lw=2.8, alpha=0.9
                    )
                )
                # Step number at midpoint
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.annotate(
                    str(k + 1), xy=(mx, my), fontsize=7,
                    ha="center", va="center",
                    bbox=dict(
                        boxstyle="round,pad=0.2", facecolor="#FFCDD2", alpha=0.85
                    )
                )

        # ---------- Nodes ----------
        for state in solver._all_states:
            x, y = self._barycentric(state)

            if state == solver.start:
                color, size, z = "#1565C0", 240, 5   # Blue – start
            elif state == solver.goal:
                color, size, z = "#2E7D32", 240, 5   # Green – goal
            elif state in solution_nodes:
                color, size, z = "#E53935", 170, 4   # Red – on solution path
            else:
                color, size, z = "#9E9E9E", 80, 3    # Grey – other states

            ax.scatter(x, y, c=color, s=size, zorder=z,
                       edgecolors="white", linewidths=1.2)

            label = ",".join(str(v) for v in state)
            ax.annotate(label, xy=(x, y + 0.028), fontsize=6,
                        ha="center", va="bottom", color="#333333")

        # ---------- Legend ----------
        legend_items = [
            mpatches.Patch(color="#1565C0", label=f"Start: {solver.start}"),
            mpatches.Patch(color="#2E7D32", label=f"Goal: {solver.goal}"),
            mpatches.Patch(color="#E53935", label="Solution Path"),
            mpatches.Patch(color="#9E9E9E", label="Other States"),
        ]
        ax.legend(handles=legend_items, loc="upper right", fontsize=10, framealpha=0.9)

        ax.set_title(
            f"Water Jug Problem – State Space Triangle\n"
            f"Capacities: {solver.capacities}  |  "
            f"Total States: {len(solver._all_states)}  |  "
            f"Total Water: {solver.total_water}L",
            fontsize=13, fontweight="bold", pad=15
        )
        ax.set_xlim(-0.15, 1.15)
        ax.set_ylim(-0.15, math.sqrt(3) / 2 + 0.15)
        ax.axis("off")
        plt.tight_layout()

        filename = "state_space_triangle.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"\n  [OK] Figure saved as '{filename}'.")
        plt.show()

    # -----------------------------------------------------------------
    #  N-Jug – NetworkX Graph Visualization
    # -----------------------------------------------------------------
    def _draw_graph(self, solution_path=None):
        """
        Draws the state space as a NetworkX spring-layout directed graph.
        Used when the number of jugs is not 3.
        """
        solver = self.solver
        G      = self._nx_graph

        fig, ax = plt.subplots(figsize=(16, 12))
        pos     = nx.spring_layout(G, k=2.5, iterations=120, seed=42)

        # Collect solution edges and nodes
        solution_edges = set()
        solution_nodes = set()
        if solution_path:
            solution_nodes = set(solution_path)
            for k in range(len(solution_path) - 1):
                solution_edges.add((solution_path[k], solution_path[k + 1]))

        # Regular edges (grey, thin)
        other_edges = [(u, v) for u, v in G.edges() if (u, v) not in solution_edges]
        nx.draw_networkx_edges(
            G, pos, edgelist=other_edges,
            edge_color="#CCCCCC", alpha=0.3, arrows=True, ax=ax
        )

        # Solution path edges (red, thick)
        if solution_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=list(solution_edges),
                edge_color="#D32F2F", alpha=0.9,
                width=3, arrows=True, arrowsize=15, ax=ax
            )

        # Node colors and sizes
        colors = []
        sizes  = []
        for node in G.nodes():
            if node == solver.start:
                colors.append("#1565C0"); sizes.append(500)
            elif node == solver.goal:
                colors.append("#2E7D32"); sizes.append(500)
            elif node in solution_nodes:
                colors.append("#E53935"); sizes.append(350)
            else:
                colors.append("#BDBDBD"); sizes.append(200)

        nx.draw_networkx_nodes(
            G, pos, node_color=colors, node_size=sizes,
            edgecolors="white", linewidths=1.5, ax=ax
        )
        nx.draw_networkx_labels(
            G, pos, {n: str(n) for n in G.nodes()}, font_size=7, ax=ax
        )

        # Legend
        legend_items = [
            mpatches.Patch(color="#1565C0", label=f"Start: {solver.start}"),
            mpatches.Patch(color="#2E7D32", label=f"Goal: {solver.goal}"),
            mpatches.Patch(color="#E53935", label="Solution Path"),
            mpatches.Patch(color="#BDBDBD", label="Other States"),
        ]
        ax.legend(handles=legend_items, loc="upper right", fontsize=10)
        ax.set_title(
            f"Water Jug Problem – State Space Graph\n"
            f"Capacities: {solver.capacities}  |  "
            f"Total States: {len(solver._all_states)}",
            fontsize=14, fontweight="bold"
        )
        ax.axis("off")
        plt.tight_layout()

        filename = "state_space_graph.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"\n  [OK] Figure saved as '{filename}'.")
        plt.show()


# ===========================================================================
#  MAIN ENTRY POINT  (console output + visualization)
# ===========================================================================

def main():
    """
    Full demo entry point: collects user input, runs both solving methods,
    prints console output, and renders the state space visualization.
    """
    line = "=" * 70

    print(f"\n{line}")
    print("  WATER JUG PROBLEM SOLVER  –  Visualized Demo")
    print("  Graduate Course: Heuristic Problem Solving Methods")
    print(f"{line}\n")

    print("  Enter jug capacities separated by commas.")
    print("  The number of jugs is set by the count of values you enter.\n")
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

    # Console output
    solver.print_solution(method="bfs")
    solver.print_solution(method="state_space")
    solver.print_state_space()

    # Visualization
    states, _ = solver.solve_via_state_space()
    visualizer = WaterJugVisualizer(solver)
    visualizer.draw(solution_path=states)


if __name__ == "__main__":
    main()
