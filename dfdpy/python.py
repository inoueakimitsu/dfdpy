"""Generate DFDs from Python source code.
"""
import ast
import html
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple, Union


@dataclass
class ProcessNode:
    """Node for process or data.
    """
    code: str
    line_number: int


@dataclass
class DataStoreNode:
    """Node for process or data.
    """
    code: str
    line_number: int
    version: int


def make_dfd(
        source: str,
        hidden_id_list: Sequence[str]) -> tuple[
            list[ProcessNode], list[DataStoreNode],
            list[Tuple[
                Union[ProcessNode, DataStoreNode],
                Union[ProcessNode, DataStoreNode]]]]:

    tree = ast.parse(source)
    already_written_edges: List[
        Tuple[Union[ProcessNode,
                    DataStoreNode], Union[ProcessNode, DataStoreNode]]] = []
    shown_node_id_with_version: Dict[str, int] = {}

    process_node_list: List[ProcessNode] = []
    data_store_node_list: List[DataStoreNode] = []
    edges: List[Tuple[
        Union[ProcessNode, DataStoreNode],
        Union[ProcessNode, DataStoreNode]]] = []

    for name in tree._fields:
        for node in getattr(tree, name):
            if isinstance(node, ast.Assign):
                # lhs
                lhs_id_list = []
                lhs_node_list = []
                for target in node.targets:
                    for lhs_child_node in ast.walk(target):
                        if isinstance(lhs_child_node, ast.Name):
                            lhs_id_list.append(lhs_child_node.id)
                            lhs_node_list.append(lhs_child_node)

                # rhs
                rhs_id_list = []
                rhs_node_list = []
                for rhs_child_node in ast.walk(node.value):
                    if isinstance(rhs_child_node, ast.Name):
                        rhs_id_list.append(rhs_child_node.id)
                        rhs_node_list.append(rhs_child_node)

                # process
                if not rhs_node_list:
                    continue

                process_code_str = ast.get_source_segment(source, node)
                if process_code_str is None:
                    process_code_str = ""

                # Remove isolated process node.
                if all(
                        (rhs_node.id in hidden_id_list for rhs_node in rhs_node_list)) or \
                        all((lhs_node.id in hidden_id_list for lhs_node in lhs_node_list)):
                    continue

                current_process_node = ProcessNode(
                    code=process_code_str,
                    line_number=node.lineno)

                process_node_list.append(current_process_node)

                for rhs_node in rhs_node_list:
                    if rhs_node.id not in shown_node_id_with_version:
                        shown_node_id_with_version[rhs_node.id] = 0

                for lhs_node in lhs_node_list:
                    for rhs_node in rhs_node_list:
                        if rhs_node.id in hidden_id_list:
                            continue
                        if lhs_node.id in hidden_id_list:
                            continue

                        rhs_node_with_version: DataStoreNode = DataStoreNode(
                            code=rhs_node.id,
                            line_number=rhs_node.lineno,
                            version=shown_node_id_with_version[rhs_node.id])

                        if (rhs_node_with_version, current_process_node) not in already_written_edges:
                            edges.append(
                                (rhs_node_with_version, current_process_node))
                            already_written_edges.append(
                                (rhs_node_with_version, current_process_node))
                            data_store_node_list.append(rhs_node_with_version)

                for lhs_node in lhs_node_list:
                    if lhs_node.id not in shown_node_id_with_version:
                        shown_node_id_with_version[lhs_node.id] = 0
                    else:
                        shown_node_id_with_version[lhs_node.id] += 1

                for lhs_node in lhs_node_list:
                    for rhs_node in rhs_node_list:
                        if rhs_node.id in hidden_id_list:
                            continue
                        if lhs_node.id in hidden_id_list:
                            continue

                        lhs_node_with_version: DataStoreNode = DataStoreNode(
                            code=lhs_node.id,
                            line_number=lhs_node.lineno,
                            version=shown_node_id_with_version[lhs_node.id])

                        if (current_process_node, lhs_node_with_version) not in already_written_edges:
                            edges.append(
                                (current_process_node, lhs_node_with_version))
                            already_written_edges.append(
                                (current_process_node, lhs_node_with_version))
                            data_store_node_list.append(lhs_node_with_version)
    return process_node_list, data_store_node_list, edges


class MermaidJsGraphExporter:
    """Export DFD to Mermaid.js graph.
    """
    def __init__(self, graph_orientation: str = "LR") -> None:
        self._graph_orientation = graph_orientation

    def export(
        self,
        process_node_list: List[ProcessNode],
        data_store_node_list: List[DataStoreNode],
        edges: list[Tuple[
            Union[ProcessNode, DataStoreNode],
            Union[ProcessNode, DataStoreNode]]]) -> str:

        graph_expressions: List[str] = [f"graph {self._graph_orientation};"]

        # write process node list
        for process_node in process_node_list:
            process_node_expression = self._get_process_node_expression(
                process_node)
            graph_expressions.append(process_node_expression)

        # write data store node list
        for data_store_node in data_store_node_list:
            data_store_node_expression = self._get_data_store_node_expression(
                data_store_node)
            graph_expressions.append(data_store_node_expression)

        # write edges
        for edge in edges:
            edge_expression = self._get_edge_expression(edge)
            graph_expressions.append(edge_expression)

        return "\n".join(graph_expressions)

    def _get_edge_expression(self, edge: Tuple[Union[ProcessNode, DataStoreNode], Union[ProcessNode, DataStoreNode]]) -> str:
        if isinstance(edge[0], ProcessNode) and isinstance(edge[1], DataStoreNode):
            return f'{self._get_process_node_identifier(edge[0])} --> {self._get_data_store_node_identifier(edge[1])};'
        if isinstance(edge[0], DataStoreNode) and isinstance(edge[1], ProcessNode):
            return f'{self._get_data_store_node_identifier(edge[0])} --> {self._get_process_node_identifier(edge[1])};'
        raise ValueError(f'Invalid edge: {edge}')

    def _get_process_node_expression(self, process_node):
        escaped_code: str = html.escape(process_node.code)
        output_str = f'{self._get_process_node_identifier(process_node)}("{escaped_code}");'
        return output_str

    def _get_process_node_identifier(self, process_node):
        return f'L{process_node.line_number}'

    def _get_data_store_node_identifier(self, data_store_node):
        return html.escape(data_store_node.code) + "'" * data_store_node.version

    def _get_data_store_node_expression(self, data_store_node):
        identifier = self._get_data_store_node_identifier(data_store_node)
        output_str = f'{identifier}["{identifier}"];'
        return output_str
