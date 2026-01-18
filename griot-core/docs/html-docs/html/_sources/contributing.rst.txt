Contributing
============

We welcome contributions to Griot Core! This guide will help you get started.

Development Setup
-----------------

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/your-org/griot.git
   cd griot/griot-core

2. Create a virtual environment:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install development dependencies:

.. code-block:: bash

   pip install -e ".[all,dev]"

4. Verify installation:

.. code-block:: bash

   python -c "import griot_core; print(griot_core.__version__)"

Project Structure
-----------------

.. code-block:: text

   griot-core/
   ├── src/
   │   └── griot_core/
   │       ├── __init__.py          # Public API exports
   │       ├── _utils.py            # Internal utilities
   │       ├── constraints.py       # Field constraints
   │       ├── contract.py          # Contract class
   │       ├── dataframe_validation.py  # Pandera integration
   │       ├── exceptions.py        # Custom exceptions
   │       ├── linter.py            # Contract linting
   │       ├── manifest.py          # Manifest generation
   │       ├── mock.py              # Mock data generation
   │       ├── reports.py           # Report generation
   │       ├── schema.py            # Schema class
   │       └── types.py             # Type definitions & enums
   ├── tests/
   │   └── ...                      # Test files
   ├── docs/
   │   └── source/                  # Sphinx documentation
   ├── pyproject.toml               # Project configuration
   └── README.md

Code Style
----------

We use the following tools:

- **Black** - Code formatting
- **isort** - Import sorting
- **Ruff** - Linting
- **mypy** - Type checking

Run formatters before committing:

.. code-block:: bash

   black src/ tests/
   isort src/ tests/
   ruff check src/ tests/
   mypy src/

Type Hints
^^^^^^^^^^

All public functions must have type hints:

.. code-block:: python

   # Good
   def process_schema(schema: Schema, validate: bool = True) -> dict[str, Any]:
       ...

   # Bad - missing type hints
   def process_schema(schema, validate=True):
       ...

Docstrings
^^^^^^^^^^

Use Google-style docstrings:

.. code-block:: python

   def validate_dataframe(
       df: pd.DataFrame,
       schema: type[Schema],
       coerce: bool = False,
   ) -> ValidationResult:
       """Validate a DataFrame against a schema.

       Args:
           df: The DataFrame to validate.
           schema: The schema class to validate against.
           coerce: Whether to coerce types before validation.

       Returns:
           ValidationResult containing validation status and errors.

       Raises:
           ValidationException: If validation fails and raise_on_error is True.

       Example:
           >>> result = validate_dataframe(df, MySchema)
           >>> print(result.is_valid)
           True
       """
       ...

Testing
-------

Running Tests
^^^^^^^^^^^^^

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=griot_core --cov-report=html

   # Run specific test file
   pytest tests/test_schema.py

   # Run specific test
   pytest tests/test_schema.py::test_field_definition

Writing Tests
^^^^^^^^^^^^^

- Place tests in the ``tests/`` directory
- Name test files ``test_*.py``
- Name test functions ``test_*``
- Use fixtures for common setup

.. code-block:: python

   import pytest
   from griot_core import Schema, Field, validate_dataframe

   class TestSchemaDefinition:
       """Tests for schema definition."""

       def test_basic_schema(self):
           """Schema can be defined with fields."""
           class MySchema(Schema):
               id: str = Field("ID", primary_key=True)
               name: str = Field("Name")

           assert MySchema.get_primary_key() == "id"
           assert "name" in MySchema.field_names()

       def test_schema_inheritance(self):
           """Child schemas inherit parent fields."""
           class Parent(Schema):
               id: str = Field("ID", primary_key=True)

           class Child(Parent):
               name: str = Field("Name")

           assert "id" in Child.field_names()
           assert "name" in Child.field_names()

   @pytest.fixture
   def sample_schema():
       """Fixture providing a sample schema."""
       class SampleSchema(Schema):
           id: str = Field("ID", primary_key=True)
           value: float = Field("Value")
       return SampleSchema

   def test_with_fixture(sample_schema):
       """Test using a fixture."""
       assert sample_schema.get_primary_key() == "id"

Test Coverage
^^^^^^^^^^^^^

Aim for high test coverage:

- All public functions should have tests
- Cover edge cases and error paths
- Test with different DataFrame backends when applicable

Documentation
-------------

Building Docs
^^^^^^^^^^^^^

.. code-block:: bash

   cd docs
   make html

   # Open in browser
   open build/html/index.html  # macOS
   start build/html/index.html  # Windows

Writing Docs
^^^^^^^^^^^^

Documentation uses reStructuredText (RST) format:

.. code-block:: rst

   Section Title
   =============

   Subsection
   ----------

   Paragraph text with **bold** and *italic*.

   .. code-block:: python

      # Python code example
      from griot_core import Schema

   .. note::

      Important information.

   .. warning::

      Something to be careful about.

API Documentation
^^^^^^^^^^^^^^^^^

API docs are auto-generated from docstrings. Ensure all public APIs have:

- Clear description
- Parameter documentation
- Return type documentation
- Usage examples

Pull Request Process
--------------------

1. **Fork** the repository
2. **Create a branch** for your feature/fix
3. **Write code** following the style guide
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run all checks** locally
7. **Submit PR** with a clear description

PR Checklist
^^^^^^^^^^^^

Before submitting:

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] New code has tests
- [ ] Documentation updated
- [ ] Changelog entry added (if applicable)
- [ ] PR description explains the change

Commit Messages
^^^^^^^^^^^^^^^

Use clear, descriptive commit messages:

.. code-block:: text

   Add QualityRule builder for type-safe rule creation

   - Add QualityRule dataclass with factory methods
   - Add QualityMetric, QualityOperator, QualityUnit enums
   - Update PanderaSchemaGenerator to use enums
   - Add tests for all new functionality

Release Process
---------------

Releases are handled by maintainers:

1. Update version in ``pyproject.toml``
2. Update ``CHANGELOG.rst``
3. Create release commit
4. Tag the release
5. Build and publish to PyPI

Getting Help
------------

- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check the guides and API reference

Code of Conduct
---------------

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the project's guidelines

License
-------

By contributing, you agree that your contributions will be licensed
under the same license as the project (see LICENSE file).
