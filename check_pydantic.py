import pydantic
print(f"Pydantic Version: {pydantic.VERSION}")
try:
    import pydantic.v1
    print("pydantic.v1 is available")
except ImportError:
    print("pydantic.v1 is NOT available")
