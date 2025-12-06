import sys
print(sys.executable)
print(sys.path)
try:
    import sqlalchemy
    print(f"SQLAlchemy: {sqlalchemy.__version__}")
except ImportError:
    print("SQLAlchemy not found")
try:
    import alembic
    print(f"Alembic: {alembic.__version__}")
except ImportError:
    print("Alembic not found")
