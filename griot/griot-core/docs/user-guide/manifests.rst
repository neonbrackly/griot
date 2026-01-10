Manifest Export
===============

griot-core can export contracts as manifests optimized for different consumers,
including AI/LLM systems, semantic web applications, and documentation.

Export Formats
--------------

Three export formats are available:

1. **JSON-LD**: Semantic web / linked data format
2. **Markdown**: Human-readable documentation
3. **LLM Context**: Optimized for AI/LLM consumption

Basic Export
------------

Export using the ``to_manifest()`` method:

.. code-block:: python

   from griot_core import GriotModel, Field

   class Product(GriotModel):
       """Product catalog data contract."""

       product_id: str = Field(
           description="Unique product identifier",
           primary_key=True,
           pattern=r"^PROD-\d{6}$",
           examples=["PROD-000001", "PROD-123456"]
       )
       name: str = Field(
           description="Product display name",
           max_length=255,
           examples=["Wireless Mouse", "USB-C Cable"]
       )
       price: float = Field(
           description="Product price in USD",
           ge=0.0,
           unit="USD"
       )
       category: str = Field(
           description="Product category",
           enum=["electronics", "clothing", "home", "food"]
       )

   # Export as LLM context (default)
   llm_manifest = Product.to_manifest(format="llm_context")

   # Export as JSON-LD
   jsonld_manifest = Product.to_manifest(format="json_ld")

   # Export as Markdown
   markdown_manifest = Product.to_manifest(format="markdown")

LLM Context Format
------------------

Optimized for AI/LLM prompt injection:

.. code-block:: python

   llm_manifest = Product.to_manifest(format="llm_context")
   print(llm_manifest)

Output:

.. code-block:: text

   # Data Contract: Product

   Product catalog data contract.

   ## Fields

   ### product_id (string) [PRIMARY KEY]
   Unique product identifier
   - Pattern: ^PROD-\d{6}$
   - Examples: PROD-000001, PROD-123456

   ### name (string)
   Product display name
   - Max length: 255
   - Examples: Wireless Mouse, USB-C Cable

   ### price (float)
   Product price in USD
   - Minimum: 0.0
   - Unit: USD

   ### category (string)
   Product category
   - Allowed values: electronics, clothing, home, food

   ## Constraints
   - product_id is the primary key
   - All fields are required unless marked nullable

Use in prompts:

.. code-block:: python

   prompt = f"""
   You are a data assistant. Here is the data contract you're working with:

   {llm_manifest}

   User query: Show me all electronics products under $50
   """

JSON-LD Format
--------------

Semantic web format with linked data:

.. code-block:: python

   jsonld_manifest = Product.to_manifest(format="json_ld")
   print(jsonld_manifest)

Output:

.. code-block:: json

   {
     "@context": {
       "@vocab": "https://schema.org/",
       "griot": "https://griot.dev/schema/",
       "xsd": "http://www.w3.org/2001/XMLSchema#"
     },
     "@type": "griot:DataContract",
     "@id": "griot:contract/Product",
     "name": "Product",
     "description": "Product catalog data contract.",
     "version": "1.0.0",
     "griot:fields": [
       {
         "@type": "griot:Field",
         "name": "product_id",
         "description": "Unique product identifier",
         "griot:dataType": "string",
         "griot:primaryKey": true,
         "griot:pattern": "^PROD-\\d{6}$"
       },
       {
         "@type": "griot:Field",
         "name": "name",
         "description": "Product display name",
         "griot:dataType": "string",
         "griot:maxLength": 255
       },
       {
         "@type": "griot:Field",
         "name": "price",
         "description": "Product price in USD",
         "griot:dataType": "float",
         "griot:minimum": 0.0,
         "griot:unit": "USD"
       },
       {
         "@type": "griot:Field",
         "name": "category",
         "description": "Product category",
         "griot:dataType": "string",
         "griot:enum": ["electronics", "clothing", "home", "food"]
       }
     ]
   }

Markdown Format
---------------

Human-readable documentation:

.. code-block:: python

   markdown_manifest = Product.to_manifest(format="markdown")
   print(markdown_manifest)

Output:

.. code-block:: markdown

   # Product

   Product catalog data contract.

   | Version | Owner | Last Updated |
   |---------|-------|--------------|
   | 1.0.0 | — | 2026-01-10 |

   ## Fields

   | Field | Type | Description | Constraints |
   |-------|------|-------------|-------------|
   | `product_id` | string | Unique product identifier | PK, pattern: `^PROD-\d{6}$` |
   | `name` | string | Product display name | max: 255 |
   | `price` | float | Product price in USD | >= 0.0, unit: USD |
   | `category` | string | Product category | enum: electronics, clothing, home, food |

   ## Examples

   ### product_id
   - `PROD-000001`
   - `PROD-123456`

   ### name
   - `Wireless Mouse`
   - `USB-C Cable`

Including PII Information
-------------------------

Include PII metadata in exports:

.. code-block:: python

   from griot_core import PIICategory, SensitivityLevel

   class Customer(GriotModel):
       customer_id: str = Field(description="Customer ID", primary_key=True)
       email: str = Field(
           description="Customer email",
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL
       )

   # Include PII info in manifest
   manifest = Customer.to_manifest(format="llm_context", include_pii=True)

Output includes:

.. code-block:: text

   ### email (string) [PII: EMAIL, CONFIDENTIAL]
   Customer email
   - Format: email
   - PII Category: EMAIL
   - Sensitivity: CONFIDENTIAL

Including Lineage
-----------------

Include data lineage in exports:

.. code-block:: python

   from griot_core import LineageConfig, Source, Consumer

   class AnalyticsData(GriotModel):
       class Meta:
           lineage = LineageConfig(
               sources=[Source(name="events_db", type="database")],
               consumers=[Consumer(name="dashboard", type="application")]
           )

       metric_id: str = Field(description="Metric ID")
       value: float = Field(description="Metric value")

   # Include lineage in manifest
   manifest = AnalyticsData.to_manifest(format="llm_context", include_lineage=True)

Output includes:

.. code-block:: text

   ## Data Lineage

   ### Sources
   - events_db (database)

   ### Consumers
   - dashboard (application)

Standalone Export Function
--------------------------

Use the standalone function:

.. code-block:: python

   from griot_core import export_manifest

   # Export with options
   manifest = export_manifest(
       Product,
       format="llm_context",
       include_pii=True,
       include_lineage=True,
       include_examples=True
   )

Export to File
--------------

Save manifests to files:

.. code-block:: python

   # Export to file
   with open("product_contract.md", "w") as f:
       f.write(Product.to_manifest(format="markdown"))

   # JSON-LD to file
   import json
   jsonld = Product.to_manifest(format="json_ld")
   with open("product_contract.jsonld", "w") as f:
       json.dump(json.loads(jsonld), f, indent=2)

Batch Export
------------

Export multiple contracts:

.. code-block:: python

   contracts = [Product, Customer, Order, Transaction]

   # Export all as markdown
   for contract in contracts:
       manifest = contract.to_manifest(format="markdown")
       filename = f"docs/contracts/{contract.__name__.lower()}.md"
       with open(filename, "w") as f:
           f.write(manifest)

   # Create index
   index = "# Data Contracts\n\n"
   for contract in contracts:
       index += f"- [{contract.__name__}](./{contract.__name__.lower()}.md)\n"

   with open("docs/contracts/index.md", "w") as f:
       f.write(index)

Custom Export Format
--------------------

Create custom export formats:

.. code-block:: python

   def export_as_sql_ddl(model):
       """Export contract as SQL DDL."""
       fields = model.get_fields()
       table_name = model.__name__.lower()

       ddl = f"CREATE TABLE {table_name} (\n"

       field_defs = []
       pk_fields = []

       for name, field in fields.items():
           # Map types
           sql_type = {
               "str": "VARCHAR(255)",
               "int": "INTEGER",
               "float": "DECIMAL(18,2)",
               "bool": "BOOLEAN"
           }.get(field.type_name, "TEXT")

           # Handle max_length
           if field.max_length and field.type_name == "str":
               sql_type = f"VARCHAR({field.max_length})"

           # Build definition
           nullable = "NULL" if field.nullable else "NOT NULL"
           field_defs.append(f"    {name} {sql_type} {nullable}")

           if field.primary_key:
               pk_fields.append(name)

       ddl += ",\n".join(field_defs)

       if pk_fields:
           ddl += f",\n    PRIMARY KEY ({', '.join(pk_fields)})"

       ddl += "\n);"

       return ddl

   # Use custom exporter
   ddl = export_as_sql_ddl(Product)
   print(ddl)

Output:

.. code-block:: sql

   CREATE TABLE product (
       product_id VARCHAR(255) NOT NULL,
       name VARCHAR(255) NOT NULL,
       price DECIMAL(18,2) NOT NULL,
       category VARCHAR(255) NOT NULL,
       PRIMARY KEY (product_id)
   );

Integration with AI Tools
-------------------------

Use manifests with AI/LLM tools:

.. code-block:: python

   # OpenAI example
   import openai

   manifest = Product.to_manifest(format="llm_context")

   response = openai.ChatCompletion.create(
       model="gpt-4",
       messages=[
           {
               "role": "system",
               "content": f"You are a data assistant. Contract:\n\n{manifest}"
           },
           {
               "role": "user",
               "content": "Generate 5 sample products as JSON"
           }
       ]
   )

   # Anthropic example
   import anthropic

   client = anthropic.Anthropic()

   response = client.messages.create(
       model="claude-3-opus-20240229",
       messages=[
           {
               "role": "user",
               "content": f"Given this contract:\n\n{manifest}\n\nGenerate 5 sample products."
           }
       ]
   )
