Installation
============

Requirements
------------

Griot Core requires **Python 3.10** or higher.

Basic Installation
------------------

Install the core library with pip:

.. code-block:: bash

   pip install griot-core

This installs the core library without any DataFrame validation backends.

Installing with DataFrame Backends
----------------------------------

Griot Core supports multiple DataFrame backends for validation. Install only what you need:

**pandas** (most common):

.. code-block:: bash

   pip install griot-core[pandas]

**polars** (high performance):

.. code-block:: bash

   pip install griot-core[polars]

**PySpark** (distributed computing):

.. code-block:: bash

   pip install griot-core[spark]

**Dask** (parallel computing):

.. code-block:: bash

   pip install griot-core[dask]

**Multiple backends**:

.. code-block:: bash

   pip install griot-core[pandas,polars]

**All backends**:

.. code-block:: bash

   pip install griot-core[all]

Verifying Installation
----------------------

Verify your installation:

.. code-block:: python

   import griot_core
   print(f"Griot Core version: {griot_core.__version__}")

   # Check available backends
   from griot_core import get_available_backends
   backends = get_available_backends()

   for name, info in backends.items():
       status = "Available" if info['available'] else "Not installed"
       print(f"  {name}: {status}")

Example output:

.. code-block:: text

   Griot Core version: 0.8.0
     pandas: Available
     polars: Not installed
     spark: Not installed
     dask: Not installed

Development Installation
------------------------

For development, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/your-org/griot.git
   cd griot/griot-core
   pip install -e ".[all,dev]"

Dependencies
------------

Core Dependencies
^^^^^^^^^^^^^^^^^

The core library has minimal dependencies:

- ``pyyaml`` - YAML parsing and serialization

Optional Dependencies
^^^^^^^^^^^^^^^^^^^^^

Each backend brings additional dependencies:

**pandas backend** (``griot-core[pandas]``):

- ``pandas >= 1.5.0``
- ``pandera[io] >= 0.18.0``

**polars backend** (``griot-core[polars]``):

- ``polars >= 0.19.0``
- ``pandera[polars] >= 0.18.0``

**spark backend** (``griot-core[spark]``):

- ``pyspark >= 3.3.0``
- ``pandera[pyspark] >= 0.18.0``

**dask backend** (``griot-core[dask]``):

- ``dask[dataframe] >= 2023.1.0``
- ``pandera[dask] >= 0.18.0``

Troubleshooting
---------------

**ImportError: No module named 'pandera'**

You haven't installed a DataFrame backend. Install one:

.. code-block:: bash

   pip install griot-core[pandas]

**Version conflicts**

If you encounter version conflicts, try creating a fresh virtual environment:

.. code-block:: bash

   python -m venv griot-env
   source griot-env/bin/activate  # On Windows: griot-env\Scripts\activate
   pip install griot-core[pandas]

**PySpark issues**

PySpark requires Java. Ensure you have Java 8+ installed:

.. code-block:: bash

   java -version

Next Steps
----------

- Continue to :doc:`quickstart` for a hands-on tutorial
- Learn the :doc:`concepts` behind Griot Core
