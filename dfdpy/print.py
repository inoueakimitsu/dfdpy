import ast
import html
from typing import Dict, List, Tuple

source = open("sample.py", encoding="UTF8").read()
source_splitlines = source.splitlines()
tree = ast.parse(source)

# for name in tree._fields:
#     for node in getattr(tree, name):
#         if isinstance(node, ast.Assign):
#             # lhs
#             for target in node.targets:
#                 for lhs_child_node in ast.walk(target):
#                     if isinstance(lhs_child_node, ast.Name):
#                         print("lhs:", lhs_child_node.id)

#             # rhs
#             for rhs_child_node in ast.walk(node.value):
#                 if isinstance(rhs_child_node, ast.Name):
#                     print("rhs:", rhs_child_node.id)
            
#             print(ast.dump(node, indent=2))
#             print("------------")

hidden_id_list = [
    "np",
    "len",
    "float",
    "pd",
    "nx",
    "datetime",
]
# already_written_rhs_id_list: List[str] = []
# already_written_lhs_id_list: List[str] = []
# already_written_node_abbreviation_list: List[str] = []

already_written_edge: List[Tuple[str, str]] = []

shown_node_id_with_version: Dict[str, int] = {}

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
                        # print("lhs:", lhs_child_node.id)

            # rhs
            rhs_id_list = []
            rhs_node_list = []
            for rhs_child_node in ast.walk(node.value):
                if isinstance(rhs_child_node, ast.Name):
                    rhs_id_list.append(rhs_child_node.id)
                    rhs_node_list.append(rhs_child_node)
                    # print("rhs:", rhs_child_node.id)

            lhs_id_set = set(lhs_id_list)
            rhs_id_set = set(rhs_id_list)

            # process
            if not rhs_node_list:
                continue
            
            start_line_no = node.lineno
            end_line_no = node.value.end_lineno + 1
            process_code_str = ast.get_source_segment(source, node)
            process_code_str_escaped = html.escape(process_code_str)#.replace(" ", "#nbsp;").replace("\n", "<br />")

            # 孤立した process ノードを削除します。
            if all((rhs_node.id in hidden_id_list for rhs_node in rhs_node_list)) or all((lhs_node.id in hidden_id_list for lhs_node in lhs_node_list)):
                continue
            
            node_abbreviation = f'l{node.lineno}'
            print(f'{node_abbreviation}("{process_code_str_escaped}")')
            print(f"style {node_abbreviation} text-align:left,fill:#ffffde")

            for rhs_node in rhs_node_list:
                if rhs_node.id not in shown_node_id_with_version:
                    shown_node_id_with_version[rhs_node.id] = 0

            for lhs_node in lhs_node_list:
                for rhs_node in rhs_node_list:
                    if rhs_node.id in hidden_id_list:
                        continue
                    if lhs_node.id in hidden_id_list:
                        continue
                        
                    rhs_node_id_with_version = str(rhs_node.id) + "'"*shown_node_id_with_version[rhs_node.id]
                    # lhs_node_id_with_version = str(lhs_node.id) + "'"*shown_node_id_with_version[lhs_node.id]
                    
                    if (rhs_node_id_with_version, node_abbreviation) not in already_written_edge:
                        print(f'{rhs_node_id_with_version} --> {node_abbreviation};')
                        already_written_edge.append((rhs_node_id_with_version, node_abbreviation))

                    # if (node_abbreviation, lhs_node_id_with_version) not in already_written_edge:
                    #     print(f'{node_abbreviation} --> {lhs_node_id_with_version};')
                    #     already_written_edge.append((node_abbreviation, lhs_node_id_with_version))
            
            # for lhs_node in lhs_node_list:
            #     if lhs_node.id in shown_node_id_with_version:
            #         shown_node_id_with_version[lhs_node.id] += 1

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
                        
                    # rhs_node_id_with_version = str(rhs_node.id) + "'"*shown_node_id_with_version[rhs_node.id]
                    lhs_node_id_with_version = str(lhs_node.id) + "'"*shown_node_id_with_version[lhs_node.id]
                    
                    # if (rhs_node_id_with_version, node_abbreviation) not in already_written_edge:
                    #     print(f'{rhs_node_id_with_version} --> {node_abbreviation};')
                    #     already_written_edge.append((rhs_node_id_with_version, node_abbreviation))

                    if (node_abbreviation, lhs_node_id_with_version) not in already_written_edge:
                        print(f'{node_abbreviation} --> {lhs_node_id_with_version};')
                        already_written_edge.append((node_abbreviation, lhs_node_id_with_version))