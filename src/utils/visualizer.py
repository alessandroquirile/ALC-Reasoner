from typing import Set
import os

from src.core.node import Node


def _find_satisfying_nodes(root: Node) -> Set[str]:
    path = set()
    if root.status == 'clashed':
        return path

    nodes_to_visit = [root]
    while nodes_to_visit:
        node = nodes_to_visit.pop(0)
        path.add(node.id)

        # Follow branch successors (only the satisfying branch)
        if node.branch_successors:
            for succ in node.branch_successors:
                if succ.status != 'clashed':
                    nodes_to_visit.append(succ)
                    break

        # Follow regular successors
        for role, successors in node.successors.items():
            for succ in successors:
                nodes_to_visit.append(succ)

    return path


def _get_node_label(node: Node) -> str:
    labels_str = "\\n".join([str(l) for l in sorted(node.labels, key=lambda x: str(x))])
    header = f"{node.original_id}"
    return f"{{ {header} | {labels_str} }}"


class Visualizer:
    """
    Generates Graphviz DOT representation of the tableau expansion.
    """

    def __init__(self):
        self.visited = set()
        self.dot_lines = []
        self.satisfying_nodes = set()

    def _get_node_style(self, node: Node) -> str:
        if node.status == 'clashed':
            return "color=red, fontcolor=red"
        elif node.id in self.satisfying_nodes:
            return "color=black, fontcolor=black"
        else:
            return "color=gray, fontcolor=gray"

    def build_dot(self, root: Node) -> str:
        self.visited = set()
        self.satisfying_nodes = _find_satisfying_nodes(root)
        self.dot_lines = ["digraph Tableau {", '    node [shape=record, fontname="Arial"];']
        self._traverse(root)
        self.dot_lines.append("}")
        return "\n".join(self.dot_lines)

    def _traverse(self, node: Node):
        if node.id in self.visited:
            return
        self.visited.add(node.id)

        # Add node definition
        label = _get_node_label(node)
        style = self._get_node_style(node)
        self.dot_lines.append(f'    "{node.id}" [label="{label}", {style}];')

        # Add success edges (Green if in satisfying path, gray otherwise)
        for role, successors in node.successors.items():
            for succ in successors:
                target_id = succ.id
                if node.id in self.satisfying_nodes and target_id in self.satisfying_nodes:
                    edge_style = 'color=green, fontcolor=green, label="' + role + '"'
                else:
                    edge_style = 'color=gray, fontcolor=gray, label="' + role + '"'
                self.dot_lines.append(f'    "{node.id}" -> "{target_id}" [{edge_style}];')
                self._traverse(succ)

        # Add branching edges (Green if in satisfying path, red if clashed, gray otherwise)
        for succ in node.branch_successors:
            target_id = succ.id
            if node.id in self.satisfying_nodes and target_id in self.satisfying_nodes:
                edge_style = 'color=green, style=solid, penwidth=2'
            elif succ.status == 'clashed':
                edge_style = 'color=red, style=solid, penwidth=2'
            else:
                edge_style = 'color=gray, style=solid'
            self.dot_lines.append(f'    "{node.id}" -> "{target_id}" [{edge_style}];')
            self._traverse(succ)

        # Add failed edges (Red)
        for role, failed in node.failed_successors.items():
            for f_succ in failed:
                target_id = f_succ.id
                edge_style = 'color=red, style=dashed, fontcolor=red, label="' + role + '"'
                self.dot_lines.append(f'    "{node.id}" -> "{target_id}" [{edge_style}];')
                self._traverse(f_succ)

        # Add blocking edge (Orange)
        if node.blocked_by:
            target_id = node.blocked_by.id
            edge_style = 'color=orange, style=dotted, constraint=false, label="blocked by"'
            self.dot_lines.append(f'    "{node.id}" -> "{target_id}" [{edge_style}];')

    def save_dot(self, root: Node, filename: str = "tableau.dot"):
        dot_content = self.build_dot(root)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(dot_content)
        print(f"\nTableau exported to {filename}")

    def save_png(self, root: Node, filename: str = "tableau.png", dot_filename: str = "tableau.dot"):
        self.save_dot(root, dot_filename)
        import subprocess
        try:
            # Run the dot command to generate the PNG representation
            subprocess.run(["dot", "-Tpng", dot_filename, "-o", filename], check=True)
            print(f"Tableau image successfully generated at {filename}")
        except FileNotFoundError:
            print("\n[Warning] Graphviz 'dot' command not found.")
            print("Please install Graphviz to generate PNG visualizations.")
            print(f"DOT file is available at: {dot_filename}")
        except subprocess.CalledProcessError as e:
            print(f"\n[Error] Graphviz failed to compile DOT file to PNG: {e}")
