Forum gruppeprosjekt, basert på flask demo
======

The basic blog app built in the Flask `tutorial`_.

.. _tutorial: http://flask.pocoo.org/docs/tutorial/


Install
-------

Create a virtualenv and activate it::

    python3 -m venv venv
    . venv/bin/activate

Or on Windows cmd::

    py -3 -m venv venv
    venv\Scripts\activate.bat

Install Flaskr:

    pip install -e .

Initialize database: 
    
    flask init-db

Run
---

::

    export FLASK_APP=flaskr
    export FLASK_ENV=development
    flask run --host 0.0.0.0

Or on Windows cmd::

    set FLASK_APP=flaskr
    set FLASK_ENV=development
    flask run

Open http://127.0.0.1:5000 in a browser.

Test
----

::

    pip install '.[test]'
    pytest

Run with coverage report::

    coverage run -m pytest
    coverage report
    coverage html  # open htmlcov/index.html in a browser
