# dfdpy: Python Code to DFD Converter

This project provides a GUI tool and a library to convert Python source code into a Data Flow Diagram (DFD). The GUI tool is built using Streamlit, and the library is named `dfdpy`.

![image](https://github.com/user-attachments/assets/e90fa582-a00e-4413-9214-16038c79fb73)

## Features

- Convert Python source code to a Data Flow Diagram (DFD).
- Provides a GUI for easy conversion and visualization.
- Customizable graph orientation and hidden identifier list.

## Requirements

- Python 3.10+
- Poetry for dependency management

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/inoueakimitsu/dfdpy.git
    cd dfdpy
    ```

2. Install the dependencies using Poetry:
    ```bash
    poetry install
    ```

## Usage

### GUI

To run the GUI tool, use the following command:
```bash
streamlit run viewer.py
```

This will start a Streamlit app in your web browser where you can input Python code and get the corresponding Data Flow Diagram.

### As a library

The dfdpy library can be used directly in your Python code. Below is an example of how to use it:

```python
from dfdpy.python import make_dfd, MermaidJsGraphExporter

source_code = """
np.random.seed(123)

n_classes = 15
n_bags = 200
n_max_instance_in_one_bag = 1000
n_instances_of_each_bags = [np.random.randint(low=0, high=n_max_instance_in_one_bag) for _ in range(n_bags)]
class_labels_of_instance_in_bags = generate_instance(n_classes, n_instances_of_each_bags)
count_each_class_of_instance_in_bags = [
    pd.Series(x).value_counts().to_dict() for x in class_labels_of_instance_in_bags
]
count_each_class_of_instance_in_bags_matrix = \
    pd.DataFrame(count_each_class_of_instance_in_bags)[list(range(n_classes))].values
count_each_class_of_instance_in_bags_matrix = np.nan_to_num(count_each_class_of_instance_in_bags_matrix)
lower_threshold = np.zeros_like(count_each_class_of_instance_in_bags_matrix)
upper_threshold = np.zeros_like(count_each_class_of_instance_in_bags_matrix)
divisions = [0, 50, 100, 200, 1000, n_max_instance_in_one_bag]
for i_bag in range(n_bags):
    for i_class in range(n_classes):
        positive_count = count_each_class_of_instance_in_bags_matrix[i_bag, i_class]
        for i_division in range(len(divisions)-1):
            if divisions[i_division] <= positive_count and positive_count < divisions[i_division+1]:
                lower_threshold[i_bag, i_class] = divisions[i_division]
                upper_threshold[i_bag, i_class] = divisions[i_division+1]

n_fatures = 7
x_min = 0
x_max = 100
cov_diag = 0.1*40**2

means_of_classes = [np.random.uniform(low=x_min, high=x_max, size=n_fatures) for _ in range(n_classes)]
covs_of_classes = [np.eye(n_fatures)*cov_diag for _ in range(n_classes)]
bags = [
    np.vstack([
        np.random.multivariate_normal(
            means_of_classes[class_label],
            covs_of_classes[class_label],
            size=1) for class_label in class_labels_of_instance_in_bag
    ]) for class_labels_of_instance_in_bag in class_labels_of_instance_in_bags
]

true_y = [np.array([class_label for class_label in class_labels_of_instance_in_bag]) for class_labels_of_instance_in_bag in class_labels_of_instance_in_bags]

flatten_features = np.vstack(bags)
max_n_clusters = 500
cluster_generator = MiniBatchKMeans(n_clusters=max_n_clusters, random_state=0)
insample_estimated_clusters = cluster_generator.fit_predict(flatten_features)
n_clusters = np.max(insample_estimated_clusters) + 1
print("n_clusters:", n_clusters)

cluster_encoder = OneHotEncoder(sparse=False)
cluster_encoder.fit(np.array([np.arange(n_clusters)]).T)

milclassifier = generate_mil_classifier(
    cluster_generator,
    cluster_encoder,
    bags,
    lower_threshold,
    upper_threshold,
    n_clusters)

df_confusion_matrix = pd.crosstab(np.hstack(true_y), milclassifier.predict(np.vstack(bags)))
"""

process_node_list, data_store_node_list, edges = make_dfd(source_code, hidden_id_list=[])
exporter = MermaidJsGraphExporter(graph_orientation="LR")
print(exporter.export(process_node_list=process_node_list, data_store_node_list=data_store_node_list, edges=edges))
```

This example demonstrates how to generate a DFD from a given Python source code and export it using the MermaidJsGraphExporter.
