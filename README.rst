Forum gruppeprosjekt, basert på Flask-demoen "Flaskr"
======

The basic blog app built in the Flask `tutorial`_.

.. _tutorial: http://flask.pocoo.org/docs/tutorial/


Install
-------

Start by cloning the code to the computer of your choice. This could
be done like this::

    cd
    git clone https://github.com/Ketil-A/forum
    cd forum
 
Create a virtualenv and activate it::

    python3 -m venv venv
    . venv/bin/activate

Or on Windows cmd::

    py -3 -m venv venv
    venv\Scripts\activate.bat

Install Flaskr:

    pip install -e .

Set the FLASK_APP variable:

    export FLASK_APP=flaskr

Or on Windows cmd:

    set FLASK_APP=flaskr

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
    flask run --host 0.0.0.0

Open http://127.0.0.1:5000 in a browser if you have installed locally. 
Or, if you have chosen to use alp-unicus-n02 instead, open http://192.168.210.133:5000/ .


Test
----

::

    pip install '.[test]'
    pytest

Run with coverage report::

    coverage run -m pytest
    coverage report
    coverage html  # open htmlcov/index.html in a browser
