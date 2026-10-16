"""Local tools exposed to the AI agent. No arbitrary code execution."""
import ast
import json
import operator
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).with_name('sales.db')
OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
             ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
             ast.Mod: operator.mod, ast.Pow: operator.pow}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculate(expression: str) -> str:
    """Safely evaluate basic arithmetic without eval()."""
    if len(expression) > 200:
        return 'Error: expression too long'
    def visit(node, depth=0):
        if depth > 20:
            raise ValueError('Expression too deeply nested')
        if isinstance(node, ast.Expression):
            return visit(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 1e12:
                raise ValueError('Number too large')
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
            return UNARY[type(node.op)](visit(node.operand, depth + 1))
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left, right = visit(node.left, depth + 1), visit(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError('Exponent too large')
            value = OPERATORS[type(node.op)](left, right)
            if not isinstance(value, (int, float)) or abs(value) > 1e15:
                raise ValueError('Result too large')
            return value
        raise ValueError('Only arithmetic is supported')
    try:
        return str(visit(ast.parse(expression, mode='eval')))
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as exc:
        return f'Error: {exc}'


def init_db():
    if DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript('''
        CREATE TABLE sales (id INTEGER PRIMARY KEY, product TEXT NOT NULL, quantity INTEGER NOT NULL, unit_price REAL NOT NULL);
        INSERT INTO sales (product, quantity, unit_price) VALUES
          ('Laptop', 3, 1200), ('Mouse', 20, 25), ('Keyboard', 10, 75),
          ('Monitor', 5, 300), ('Laptop', 2, 1200), ('Mouse', 10, 25);
        ''')
        conn.commit()
    finally:
        conn.close()


def query_database(sql: str) -> str:
    """Read-only SQL on a local sample database, with SQLite authorizer."""
    if len(sql) > 2000:
        return 'Error: query too long'
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    try:
        conn.set_authorizer(lambda action, p1, p2, db, trigger:
                            sqlite3.SQLITE_OK if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                                                            sqlite3.SQLITE_FUNCTION) else sqlite3.SQLITE_DENY)
        conn.set_progress_handler(lambda: 1, 10000)
        cursor = conn.execute(sql)
        if cursor.description is None:
            return 'Error: only SELECT queries are supported'
        columns = [c[0] for c in cursor.description]
        rows = cursor.fetchmany(101)
        if len(rows) > 100:
            return 'Error: limit queries to 100 rows'
        return json.dumps({'columns': columns, 'rows': rows}, ensure_ascii=False)
    except sqlite3.Error as exc:
        return f'SQL error: {exc}'
    finally:
        conn.close()


def current_time() -> str:
    return datetime.now(timezone.utc).isoformat()
