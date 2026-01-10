CI/CD Integration
=================

griot-cli is designed for seamless CI/CD integration with consistent exit codes,
machine-readable output formats, and GitHub Actions annotations.

Exit Codes
----------

All commands use consistent exit codes:

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - Code
     - Meaning
     - When Used
   * - 0
     - Success
     - Command completed successfully, all checks passed
   * - 1
     - Failure
     - Validation failed, breaking changes detected, threshold not met
   * - 2
     - Error
     - Invalid arguments, file not found, network error

Output Formats
--------------

JSON Format
~~~~~~~~~~~

Use ``--format json`` for machine-readable output:

.. code-block:: bash

   griot validate customer.yaml data.csv -f json | jq '.passed'

GitHub Format
~~~~~~~~~~~~~

Use ``--format github`` for GitHub Actions annotations:

.. code-block:: bash

   griot validate customer.yaml data.csv -f github

Produces annotations that appear inline in pull requests:

.. code-block:: text

   ::error::Row 42 - email: Invalid email format
   ::warning::Row 100 - name: Field is empty

GitHub Actions
--------------

Basic Validation
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Data Contract Validation

   on:
     push:
       branches: [main]
     pull_request:

   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.11'

         - name: Install griot-cli
           run: pip install griot-cli

         - name: Validate Contract
           run: griot lint customer.yaml --strict

         - name: Validate Data
           run: griot validate customer.yaml data/sample.csv -f github

Contract Quality Gates
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Contract Quality

   on:
     pull_request:
       paths:
         - 'contracts/**'

   jobs:
     quality:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.11'

         - name: Install griot-cli
           run: pip install griot-cli

         - name: Lint Contracts
           run: |
             for contract in contracts/*.yaml; do
               griot lint "$contract" --strict
             done

         - name: Check AI Readiness
           run: griot report ai contracts/customer.yaml --min-score 70

         - name: Check Compliance
           run: griot report audit contracts/customer.yaml --min-score 80

Breaking Change Detection
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Breaking Change Detection

   on:
     pull_request:
       paths:
         - 'contracts/**'

   jobs:
     breaking-changes:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with:
             fetch-depth: 0  # Full history for git diff

         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.11'

         - name: Install griot-cli
           run: pip install griot-cli

         - name: Check for Breaking Changes
           run: |
             # Get changed contract files
             CHANGED=$(git diff --name-only origin/main...HEAD -- 'contracts/*.yaml')

             for contract in $CHANGED; do
               if git show origin/main:"$contract" > /tmp/old.yaml 2>/dev/null; then
                 echo "Checking $contract for breaking changes..."
                 griot diff /tmp/old.yaml "$contract" --fail-on-breaking
               fi
             done

Registry Integration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Push to Registry

   on:
     push:
       branches: [main]
       paths:
         - 'contracts/**'

   jobs:
     push:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.11'

         - name: Install griot-cli
           run: pip install griot-cli

         - name: Push Contracts
           env:
             GRIOT_API_KEY: ${{ secrets.GRIOT_API_KEY }}
             GRIOT_REGISTRY_URL: ${{ secrets.GRIOT_REGISTRY_URL }}
           run: |
             for contract in contracts/*.yaml; do
               griot push "$contract" --version ${{ github.sha }}
             done

GitLab CI
---------

.. code-block:: yaml

   # .gitlab-ci.yml

   stages:
     - validate
     - quality
     - deploy

   variables:
     PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

   .griot-setup:
     image: python:3.11
     before_script:
       - pip install griot-cli
     cache:
       paths:
         - .pip-cache/

   lint:
     extends: .griot-setup
     stage: validate
     script:
       - griot lint contracts/customer.yaml --strict

   validate:
     extends: .griot-setup
     stage: validate
     script:
       - griot validate contracts/customer.yaml data/sample.csv

   quality-gate:
     extends: .griot-setup
     stage: quality
     script:
       - griot report ai contracts/customer.yaml --min-score 70
       - griot report audit contracts/customer.yaml --min-score 80
     only:
       - merge_requests

   push-to-registry:
     extends: .griot-setup
     stage: deploy
     script:
       - griot push contracts/customer.yaml --version $CI_COMMIT_SHA
     only:
       - main
     variables:
       GRIOT_API_KEY: $GRIOT_API_KEY
       GRIOT_REGISTRY_URL: $GRIOT_REGISTRY_URL

Jenkins
-------

.. code-block:: groovy

   // Jenkinsfile

   pipeline {
       agent {
           docker {
               image 'python:3.11'
           }
       }

       environment {
           GRIOT_API_KEY = credentials('griot-api-key')
           GRIOT_REGISTRY_URL = credentials('griot-registry-url')
       }

       stages {
           stage('Setup') {
               steps {
                   sh 'pip install griot-cli'
               }
           }

           stage('Lint') {
               steps {
                   sh 'griot lint contracts/customer.yaml --strict'
               }
           }

           stage('Validate') {
               steps {
                   sh 'griot validate contracts/customer.yaml data/sample.csv -f json > validation.json'
                   archiveArtifacts artifacts: 'validation.json'
               }
           }

           stage('Quality Gate') {
               steps {
                   sh 'griot report ai contracts/customer.yaml --min-score 70'
                   sh 'griot report audit contracts/customer.yaml --min-score 80'
               }
           }

           stage('Push') {
               when {
                   branch 'main'
               }
               steps {
                   sh "griot push contracts/customer.yaml --version ${env.GIT_COMMIT}"
               }
           }
       }

       post {
           failure {
               emailext(
                   subject: "Contract Validation Failed: ${env.JOB_NAME}",
                   body: "Check console output at ${env.BUILD_URL}",
                   recipientProviders: [requestor()]
               )
           }
       }
   }

Pre-commit Hooks
----------------

Using pre-commit:

.. code-block:: yaml

   # .pre-commit-config.yaml

   repos:
     - repo: local
       hooks:
         - id: griot-lint
           name: Lint Griot Contracts
           entry: griot lint --strict
           language: system
           files: 'contracts/.*\.yaml$'
           pass_filenames: true

         - id: griot-ai-readiness
           name: Check AI Readiness
           entry: griot report ai --min-score 60
           language: system
           files: 'contracts/.*\.yaml$'
           pass_filenames: true

Environment Variables
---------------------

Configure griot-cli for CI environments:

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
   * - ``GRIOT_REGISTRY_URL``
     - Registry server URL
   * - ``GRIOT_API_KEY``
     - API key for authentication
   * - ``GRIOT_COLOR``
     - Set to ``0`` to disable colors (recommended for CI)
   * - ``GRIOT_DEFAULT_FORMAT``
     - Default output format (e.g., ``json``)

Best Practices
--------------

1. **Disable colors in CI**: Set ``GRIOT_COLOR=0`` for cleaner logs
2. **Use JSON output**: Easier to parse and process
3. **Pin contract versions**: Use ``--version`` for reproducibility
4. **Cache pip dependencies**: Speed up builds
5. **Use secrets for API keys**: Never hardcode credentials
6. **Run validation in parallel**: Speed up large contract sets
7. **Archive artifacts**: Save reports for debugging
