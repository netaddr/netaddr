Setting up a Virtual Environment
================================

To get a `virtualenv` set up to run the `netaddr` test suites, do something
like the following:

    git clone git@github.com:json-schema-org/JSON-Schema-Test-Suite.git
    export JSON_SCHEMA_TEST_SUITE=$PWD/JSON-Schema-Test-Suite
    virtualenv -p python3 .
    source bin/activate
    pip install pytest jsonschema wheel[signatures]
    pytest
