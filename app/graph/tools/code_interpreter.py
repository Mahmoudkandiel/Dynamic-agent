from langchain_core.tools import tool
import io
import contextlib
import traceback

@tool
def code_interpreter(code: str) -> str:
    """
    Executes Python code safely in a local environment and returns the output.
    The code can define a variable named `result` to capture the final value.
    """
    buffer = io.StringIO()
    local_vars = {}
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, {"__builtins__": __builtins__}, local_vars)
        output = buffer.getvalue()
        result = local_vars.get("result", "")
        print(f"Code executed. Code: {code}, Result: {result}")
        return (output + str(result)).strip() or "No output."
    except Exception:
        return f"Error:\n{traceback.format_exc()}"
    finally:
        buffer.close()
