import functools
import sys
from contextlib import contextmanager
from io import StringIO

from django.db import connection, reset_queries
from django.template import Template, Context


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
        sys.stdout.seek(0)
        sys.stderr.seek(0)
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def print_sql(func):
    def _print_sql():
        try:
            time = sum([float(q['time']) for q in connection.queries])
            t = Template(
                "{{count}} quer{{count|pluralize:\"y,ies\"}} in {{time}} seconds:\n\n{% for sql in sqllog %}[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}{% if not forloop.last %}\n\n{% endif %}{% endfor %}")
            print(sys.stderr, t.render(
                Context({'sqllog': connection.queries, 'count': len(connection.queries), 'time': time})))

            # Empty the query list between TestCases.
            connection.queries = []
        except Exception:
            pass

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            reset_queries()
            res = func(*args, **kwargs)
        except Exception as e:
            _print_sql()
            raise e
        else:
            _print_sql()
        return res

    return wrapper
