try:
    from langchain.output_parsers import StructuredOutputParser
    print("Found in langchain.output_parsers")
except ImportError:
    print("Not in langchain.output_parsers")

try:
    from langchain_core.output_parsers import StructuredOutputParser
    print("Found in langchain_core.output_parsers")
except ImportError:
    print("Not in langchain_core.output_parsers")
