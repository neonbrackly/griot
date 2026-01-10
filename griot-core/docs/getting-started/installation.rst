Installation
============

Requirements
------------

- Python 3.10 or higher
- No external dependencies required (pure stdlib)

Install from PyPI
-----------------

.. code-block:: bash

   pip install griot-core

Install from Source
-------------------

.. code-block:: bash

   git clone https://github.com/griot/griot.git
   cd griot/griot-core
   pip install -e .

Verify Installation
-------------------

.. code-block:: python

   >>> import griot_core
   >>> griot_core.__version__
   '0.4.0'

Optional Dependencies
---------------------

griot-core has zero required dependencies, but you can install optional extras:

.. code-block:: bash

   # For YAML support (PyYAML)
   pip install griot-core[yaml]

   # For Parquet mock data output
   pip install griot-core[parquet]

   # All optional dependencies
   pip install griot-core[all]
