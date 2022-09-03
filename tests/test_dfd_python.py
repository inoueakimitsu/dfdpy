from dfdpy.python import make_dfd


def test_make_dfd():
    
    script = """
    a = hidden
    b = a
    c = b
    d = c
    """
    hidden_id_list = [
        "hidden",
    ]

    make_dfd(script, hidden_id_list)
    