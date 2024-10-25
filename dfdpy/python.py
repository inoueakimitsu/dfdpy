"""Generate DFDs from Python source code.
"""
import ast
import csv
from dataclasses import dataclass
from io import StringIO
from itertools import chain
from typing import Dict, List, Sequence, Tuple, Union
from xml.sax.saxutils import escape

@dataclass
class ProcessNode:
    """Node for process or data.
    """
    code: str
    line_number_begin: int
    line_number_end: int


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
        for _node in getattr(tree, name):
            lhs_id_list = []
            lhs_node_list = []
            rhs_id_list = []
            rhs_node_list = []

            # 処理中のノードの入力ノードと出力ノードのリストを取得する。
            for descendant_child in ast.walk(_node):

                # Assign
                if isinstance(descendant_child, ast.Assign):
                    # lhs
                    for target in descendant_child.targets:
                        for lhs_child_node in ast.walk(target):
                            if isinstance(lhs_child_node, ast.Name):
                                lhs_id_list.append(lhs_child_node.id)
                                lhs_node_list.append(lhs_child_node)

                    # rhs
                    for rhs_child_node in ast.walk(descendant_child.value):
                        if isinstance(rhs_child_node, ast.Name):
                            rhs_id_list.append(rhs_child_node.id)
                            rhs_node_list.append(rhs_child_node)
                
                # AnnAssign
                if isinstance(descendant_child, ast.AnnAssign) or isinstance(descendant_child, ast.AugAssign):
                    # lhs
                    for lhs_child_node in ast.walk(descendant_child.target):
                        if isinstance(lhs_child_node, ast.Name):
                            lhs_id_list.append(lhs_child_node.id)
                            lhs_node_list.append(lhs_child_node)

                    # rhs
                    for rhs_child_node in ast.walk(descendant_child.value):
                        if isinstance(rhs_child_node, ast.Name):
                            rhs_id_list.append(rhs_child_node.id)
                            rhs_node_list.append(rhs_child_node)

                # AugAssign
                if isinstance(descendant_child, ast.AugAssign):
                    # lhs
                    for lhs_child_node in ast.walk(descendant_child.target):
                        if isinstance(lhs_child_node, ast.Name):
                            lhs_id_list.append(lhs_child_node.id)
                            lhs_node_list.append(lhs_child_node)

                    # rhs
                    for rhs_child_node in chain(ast.walk(descendant_child.value), ast.walk(descendant_child.target)):
                        if isinstance(rhs_child_node, ast.Name):
                            rhs_id_list.append(rhs_child_node.id)
                            rhs_node_list.append(rhs_child_node)

                # For
                if isinstance(descendant_child, ast.For):
                    # lhs
                    for lhs_child_node in ast.walk(descendant_child.target):
                        if isinstance(lhs_child_node, ast.Name):
                            lhs_id_list.append(lhs_child_node.id)
                            lhs_node_list.append(lhs_child_node)

                    # rhs
                    for rhs_child_node in ast.walk(descendant_child.iter):
                        if isinstance(rhs_child_node, ast.Name):
                            rhs_id_list.append(rhs_child_node.id)
                            rhs_node_list.append(rhs_child_node)

            # process
            if not rhs_node_list:
                continue

            process_code_str = ast.get_source_segment(source, _node)
            if process_code_str is None:
                process_code_str = ""

            # Remove isolated process node.
            if all(
                    (rhs_node.id in hidden_id_list for rhs_node in rhs_node_list)) or \
                    all((lhs_node.id in hidden_id_list for lhs_node in lhs_node_list)):
                continue

            current_process_node = ProcessNode(
                code=process_code_str,
                line_number_begin=_node.lineno,
                line_number_end=_node.end_lineno)

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
            # To prevent multiple edges from being generated between the same node,
            # register only if the same record is not already registered.            
            if edge_expression not in graph_expressions:
                graph_expressions.append(edge_expression)

        return "\n".join(graph_expressions)

    def _get_edge_expression(self, edge: Tuple[Union[ProcessNode, DataStoreNode], Union[ProcessNode, DataStoreNode]]) -> str:
        if isinstance(edge[0], ProcessNode) and isinstance(edge[1], DataStoreNode):
            return f'{self._get_process_node_identifier(edge[0])} --> {self._get_data_store_node_identifier(edge[1])};'
        if isinstance(edge[0], DataStoreNode) and isinstance(edge[1], ProcessNode):
            return f'{self._get_data_store_node_identifier(edge[0])} --> {self._get_process_node_identifier(edge[1])};'
        raise ValueError(f'Invalid edge: {edge}')

    def _get_process_node_expression(self, process_node):
        escaped_code: str = escape(process_node.code, entities={
            "'": "&apos;",
            "\"": "&quot;",
            " ": "&nbsp;",
        }).replace("\n", "<br />")
        output_str = f'{self._get_process_node_identifier(process_node)}("{escaped_code}' + \
            f'<br />[Line {process_node.line_number_begin}-{process_node.line_number_end}]");' + \
            f'\nstyle {self._get_process_node_identifier(process_node)} text-align:left;'
        return output_str

    def _get_process_node_identifier(self, process_node):
        return f'L{process_node.line_number_begin}-L{process_node.line_number_end}'

    def _get_data_store_node_identifier(self, data_store_node):
        return escape(data_store_node.code, entities={
            "'": "&apos;",
            "\"": "&quot;",
            " ": "&nbsp;",
        }) + "'" * data_store_node.version

    def _get_data_store_node_expression(self, data_store_node):
        identifier = self._get_data_store_node_identifier(data_store_node)
        output_str = f'{identifier}["{identifier}"];'
        return output_str


class DrawIOGraphExporter:
    def __init__(self):
        self.csv_content = []
        self.node_id_map = {}
        self.node_refs = {}
        self.node_types = {}
        self.next_id = 1

    def export(
        self,
        process_node_list: List[ProcessNode],
        data_store_node_list: List[DataStoreNode],
        edges: List[Tuple[Union[ProcessNode, DataStoreNode], Union[ProcessNode, DataStoreNode]]]
    ) -> str:
        self._add_csv_header()
        self._add_configuration()
        self._prepare_nodes(process_node_list, data_store_node_list)
        self._prepare_edges(edges)
        self._add_csv_data()
        return self._get_csv_string()

    def _add_csv_header(self):
        self.csv_content.append("## Data Flow Diagram")

    def _add_configuration(self):
        config = [
            "# label: %name%",
            "# style: shape=%shape%;fillColor=%fill%;strokeColor=%stroke%;wrap;html=1;align=left;verticalAlign=top;rounded=%rounded%;arcSize=10;spacing=8;",
            "# namespace: csvimport-",
            "# connect: {\"from\": \"refs\", \"to\": \"id\", \"invert\": false, \"style\": \"curved=1;fontSize=11;\"}",
            "# width: auto",
            "# height: auto",
            "# padding: 15",
            "# ignore: id,shape,fill,stroke",
            "# nodespacing: 40",
            "# levelspacing: 100",
            "# edgespacing: 40",
            "# layout: horizontalflow"
        ]
        self.csv_content.extend(config)

    def _prepare_nodes(self, process_node_list: List[ProcessNode], data_store_node_list: List[DataStoreNode]):
        for node in process_node_list:
            self._add_node(node, "process")
        for node in data_store_node_list:
            self._add_node(node, "data_store")

    def _add_node(self, node: Union[ProcessNode, DataStoreNode], node_type: str):
        node_id = self._get_next_id()
        node_name = self._get_node_name(node)
        self.node_id_map[node_name] = node_id
        self.node_refs[node_id] = []
        self.node_types[node_id] = node_type

    def _prepare_edges(self, edges: List[Tuple[Union[ProcessNode, DataStoreNode], Union[ProcessNode, DataStoreNode]]]):
        for edge in edges:
            from_node = self._get_node_name(edge[0])
            to_node = self._get_node_name(edge[1])
            from_id = self.node_id_map.get(from_node, "")
            to_id = self.node_id_map.get(to_node, "")
            if from_id and to_id:
                self.node_refs[from_id].append(to_id)

    def _add_csv_data(self):
        self.csv_content.append("## CSV data starts below this line")
        self.csv_content.append("id,name,shape,fill,stroke,rounded,refs")
        
        for node_name, node_id in self.node_id_map.items():
            node_type = self.node_types[node_id]
            shape = "rectangle"
            fill = "#dae8fc" if node_type == "process" else "#d5e8d4"
            stroke = "#6c8ebf" if node_type == "process" else "#82b366"
            rounded = "1" if node_type == "process" else "0"
            refs = '"' + ",".join(self.node_refs[node_id]) + '"'
            csv_row = [
                node_id,
                self._escape_csv_field(node_name),
                shape,
                fill,
                stroke,
                rounded,
                refs,
            ]
            # To prevent multiple edges from being generated between the same node,
            # register only if the same record is not already registered.
            csv_row_str: str = ",".join(map(str, csv_row))
            if csv_row_str not in self.csv_content:
                self.csv_content.append(csv_row_str)

    def _get_node_name(self, node: Union[ProcessNode, DataStoreNode]) -> str:
        if isinstance(node, ProcessNode):
            return self._format_process_node(node)
        elif isinstance(node, DataStoreNode):
            return f"{node.code}{'_' * node.version}"
        else:
            raise ValueError(f"Invalid node type: {type(node)}")

    def _format_process_node(self, node: ProcessNode) -> str:
        code_lines = node.code.split('\n')
        formatted_code = '<br>'.join(line.replace(" ", "&nbsp;").strip() for line in code_lines if line.strip())
        return f"{formatted_code} [L{node.line_number_begin}-{node.line_number_end}]"

    def _escape_csv_field(self, field: str) -> str:
        if isinstance(field, str):
            field = field.replace('"', '""')  # エスケープダブルクォーテーション
            if ',' in field or '"' in field or '\n' in field:
                return f'"{field}"'
        return field

    def _get_csv_string(self) -> str:
        return '\n'.join(self.csv_content)

    def _get_next_id(self) -> str:
        id_str = str(self.next_id)
        self.next_id += 1
        return id_str
