import textwrap

from dfdpy.python import make_dfd, MermaidJsGraphExporter


def test_make_dfd():
    
    script = textwrap.dedent("""\
a = b
b = c
if c == d:
    e = f
elif c == e:
    e = g
else:
    if g == h:
        h = i
    else:
        h = j
    k = g
def func(x):
    s = x*2
    ss = x**3
    sss = s + ss
    return sss
k = k + func(a)
""")
    hidden_id_list = [
        "hidden",
    ]

    graph = make_dfd(script, hidden_id_list)
    print(graph)
    exporter = MermaidJsGraphExporter()
    graph_expression = exporter.export(*graph)
    print(graph_expression)
    
    