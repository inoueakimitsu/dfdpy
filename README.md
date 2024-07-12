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
import numpy as np

np.random.seed(42)
data = np.random.randn(100, 3)
mean = np.mean(data, axis=0)
std_dev = np.std(data, axis=0)
normalized_data = (data - mean) / std_dev
cov_matrix = np.cov(normalized_data, rowvar=False)
print(cov_matrix)
"""

process_node_list, data_store_node_list, edges = make_dfd(source_code, hidden_id_list=[])
exporter = MermaidJsGraphExporter(graph_orientation="LR")
print(exporter.export(process_node_list=process_node_list, data_store_node_list=data_store_node_list, edges=edges))
```

This example demonstrates how to generate a DFD from a given Python source code and export it using the MermaidJsGraphExporter.
