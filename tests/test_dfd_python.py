import textwrap

from dfdpy.python import make_dfd, MermaidJsGraphExporter


def test_make_dfd():
    
    script = textwrap.dedent("""\
    a = hidden
    b = a
    c = b
    d = c
    """)
    hidden_id_list = [
        "hidden",
    ]

    graph = make_dfd(script, hidden_id_list)
    print(graph)
    exporter = MermaidJsGraphExporter()
    graph_expression = exporter.export(*graph)
    print(graph_expression)
    
    