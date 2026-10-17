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


def get_sql_command(schema: str, table_name: str, distinct: bool = False, fields: list = None, filters: list = None,
                    filter_operator: str = "ALL", order: list = None, limit: int = None):
    """
        This creates SQL command as a string and all the data as a tuple.

    Args:
        schema: str: Description
        table_name: str: Description
        distinct: bool: Description
        fields: list: Description
        filters: list: Description
        filter_operator: str: Description
        order: list: Description
        limit: int: Description

    Returns:
        str, tuple: SQL command with data as a tuple.

    """
    if fields is None:
        fields = []
    sql = "SELECT"

    if distinct:
        sql += " DISTINCT"

    if fields:
        columns_clause = ", ".join([f'"{f}"' for f in fields])
    else:
        columns_clause = "*"

    sql += f' {columns_clause} FROM "{schema}"."{table_name}"'
    params = []

    sg_operator_map = {
        "is": "=", "is_not": "!=", "greater_than": ">", "less_than": "<", "in": "IN", "not_in": "NOT IN",
        "contains": "LIKE", "not_contains": "NOT LIKE", "starts_with": "LIKE", "ends_with": "LIKE",
        "between": "BETWEEN", "is_null": "IS NULL", "is_not_null": "IS NOT NULL"
    }

    if filters:
        conditions = []
        for flt in filters:
            if len(flt) == 2 and flt[1] in ("is_null", "is_not_null"):
                field_path, relation = flt
                val = None
            elif len(flt) == 3:
                field_path, relation, val = flt
            else:
                raise ValueError(f"Invalid filter format: {flt}")

            sql_op = sg_operator_map[relation]
            quoted_field = f'"{field_path}"'

            if relation in ("is_null", "is_not_null"):
                conditions.append(f"{quoted_field} {sql_op}")
            elif relation in ("in", "not_in"):
                if not isinstance(val, (list, tuple)):
                    val = [val]
                placeholders = ", ".join(["%s"] * len(val))
                conditions.append(f"{quoted_field} {sql_op} ({placeholders})")
                params.extend(val)
            elif relation == "contains":
                conditions.append(f"{quoted_field} LIKE %s")
                params.append(f"%{val}%")
            elif relation == "starts_with":
                conditions.append(f"{quoted_field} LIKE %s")
                params.append(f"{val}%")
            elif relation == "ends_with":
                conditions.append(f"{quoted_field} LIKE %s")
                params.append(f"%{val}")
            elif relation == "between":
                conditions.append(f"{quoted_field} BETWEEN %s AND %s")
                params.extend(val)
            else:
                conditions.append(f"{quoted_field} {sql_op} %s")
                params.append(val)

        join_str = " AND " if filter_operator.lower() == "ALL" else " OR "
        sql += " WHERE " + join_str.join(conditions)

    # order as: [{'field_name': 'code', 'direction': 'asc'}]
    if order:
        order_clauses = []
        for item in order:
            field_name = item.get("field_name")
            direction = item.get("direction", "asc").upper()

            # Validate direction to prevent SQL injection in identifier clauses
            if direction not in ("ASC", "DESC"):
                raise ValueError(f"Invalid sort direction: {direction}")

            order_clauses.append(f'"{field_name}" {direction}')

        sql += " ORDER BY " + ", ".join(order_clauses)

    if limit is not None:
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("Limit must be a non-negative integer.")

        sql += " LIMIT %s"
        params.append(limit)

    return sql, tuple(params)
