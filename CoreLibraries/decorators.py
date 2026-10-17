#  MIT License
#  Copyright (c) 2026 Sudeepth Patinjarayil
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import psycopg
from psycopg.rows import dict_row
from functools import wraps


def db_connect(database: str):
    """
        Decorator used to connect to PostgreSQL database. This will add cursor object as keyword argument and returned
        with the wrapped function.

    Args:
        database: str: Database name to which the connection will be made.

    Returns:
        None: None

    """

    def method_decorator(fns):
        @wraps(fns)
        def wrapper(*args, **kwargs):
            db_config = {
                "host": "localhost",
                "dbname": database,
                "user": "postgres",
                "password": "postgres",
                "port": "5432"
            }
            with psycopg.connect(**db_config) as connection:
                with connection.cursor(row_factory=dict_row) as cursor:
                    try:
                        kwargs["cursor"] = cursor
                        return fns(*args, **kwargs)
                    except Exception as e:
                        print(f"[Error]: Transacting while communicating to database. The detailed are: {e}")
                        raise

        return wrapper

    return method_decorator
