import textwrap

from dfdpy.python import make_dfd, MermaidJsGraphExporter


def test_make_dfd():

    script = textwrap.dedent("""\
# Prepare single-instance supervised-learning algorithm
# Note: only supports models with predict_proba() method.
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression()

# Wrap it with MilCountBasedMultiClassLearner
from milwrap import MilCountBasedMultiClassLearner 
learner: MilCountBasedMultiClassLearner = MilCountBasedMultiClassLearner(clf)

# Prepare follwing dataset
#
# - bags ... list of np.ndarray
#            (num_instance_in_the_bag * num_features)
# - lower_threshold ... np.ndarray (num_bags * num_classes)
# - upper_threshold ... np.ndarray (num_bags * num_classes)
#
# bags[i_bag] contains not less than lower_thrshold[i_bag, i_class]
# i_class instances.

# run multiple instance learning
clf_mil, y_mil = learner.fit(
    bags,
    lower_threshold,
    upper_threshold,
    n_classes,
    max_iter=10)

# after multiple instance learning,
# you can predict instance class
clf_mil.predict([instance_feature])
clf += y_mil
        """)
    hidden_id_list = [
        "hidden"
    ]

    graph = make_dfd(script, hidden_id_list)
    print(graph)
    exporter = MermaidJsGraphExporter(graph_orientation="TD")
    graph_expression = exporter.export(*graph)
    print(graph_expression)
