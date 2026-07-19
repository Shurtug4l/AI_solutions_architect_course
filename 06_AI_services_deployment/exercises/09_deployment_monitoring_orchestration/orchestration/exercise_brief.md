The goal of today's exercise is to use the branching operator (if/else)
in the Airflow DAG built together during the practice lessons.

Specifically, check that the load_dataset task actually returns a path;
if it returns a null path, make the DAG fail and raise a Python
exception explaining what happened.
