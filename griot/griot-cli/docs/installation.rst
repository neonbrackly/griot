Installation
============

Requirements
------------

- Python 3.10 or higher
- pip (Python package installer)

Installing griot-cli
--------------------

Install from PyPI
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install griot-cli

Install with Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For Parquet file support:

.. code-block:: bash

   pip install griot-cli[parquet]

For development:

.. code-block:: bash

   pip install griot-cli[dev]

Install from Source
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/griot/griot.git
   cd griot/griot-cli
   pip install -e .

Verifying Installation
----------------------

After installation, verify griot-cli is available:

.. code-block:: bash

   griot --version

You should see output like:

.. code-block:: text

   griot-cli, version 0.1.0

Shell Completion
----------------

griot-cli supports shell completion for Bash, Zsh, and Fish.

Bash
~~~~

Add to your ``~/.bashrc``:

.. code-block:: bash

   eval "$(_GRIOT_COMPLETE=bash_source griot)"

Or generate a completion script:

.. code-block:: bash

   _GRIOT_COMPLETE=bash_source griot > ~/.griot-complete.bash
   echo ". ~/.griot-complete.bash" >> ~/.bashrc

Zsh
~~~

Add to your ``~/.zshrc``:

.. code-block:: bash

   eval "$(_GRIOT_COMPLETE=zsh_source griot)"

Or generate a completion script:

.. code-block:: bash

   _GRIOT_COMPLETE=zsh_source griot > ~/.griot-complete.zsh
   echo ". ~/.griot-complete.zsh" >> ~/.zshrc

Fish
~~~~

Add to your Fish config:

.. code-block:: bash

   _GRIOT_COMPLETE=fish_source griot > ~/.config/fish/completions/griot.fish

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade griot-cli

Uninstalling
------------

To remove griot-cli:

.. code-block:: bash

   pip uninstall griot-cli

Dependencies
------------

griot-cli depends on:

- **griot-core**: Core data contract library (automatically installed)
- **click**: Command-line interface framework
- **PyYAML**: YAML parsing (optional, for config files)

All dependencies are automatically installed when you install griot-cli.
