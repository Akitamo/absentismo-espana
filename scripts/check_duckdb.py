import sys
try:
    import duckdb  # type: ignore
    print("INSTALLED", getattr(duckdb, "__version__", "unknown"))
except Exception as e:
    print("MISSING", str(e))
    sys.exit(1)
