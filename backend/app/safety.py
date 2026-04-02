"""
AST-based code safety validator
Ensures generated code only uses safe pandas/numpy/matplotlib operations
"""
import ast
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Whitelist of allowed modules
ALLOWED_MODULES = {"pandas", "numpy", "matplotlib", "math", "itertools"}

# Blacklist of dangerous function names
DANGEROUS_NAMES = {
    "eval", "exec", "compile", "__import__", 
    "open", "input", "raw_input",
    "getattr", "setattr", "delattr", "hasattr",
    "globals", "locals", "vars", "dir",
    "__builtins__", "__dict__", "__class__"
}

# Blacklist of dangerous modules
DANGEROUS_MODULES = {
    "os", "sys", "subprocess", "socket", "urllib", "requests",
    "ctypes", "multiprocessing", "threading", "importlib",
    "pickle", "shelve", "marshal", "imp", "builtins"
}


def is_safe_pandas(code: str) -> Tuple[bool, str]:
    """
    Validate that code is safe to execute
    
    Uses AST parsing to detect:
    - Dangerous imports (os, subprocess, socket, etc.)
    - Dangerous function calls (eval, exec, open, etc.)
    - Dunder method access (__globals__, __dict__, etc.)
    - Suspicious attribute access patterns
    
    Args:
        code: Python code string to validate
    
    Returns:
        Tuple of (is_safe: bool, reason: str)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Parse error: {e}"
    
    # Walk through all AST nodes
    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_base = alias.name.split(".")[0]
                if module_base not in ALLOWED_MODULES:
                    return False, f"Disallowed import: {alias.name}"
        
        if isinstance(node, ast.ImportFrom):
            if node.module:
                module_base = node.module.split(".")[0]
                if module_base not in ALLOWED_MODULES:
                    return False, f"Disallowed import from: {node.module}"
                if module_base in DANGEROUS_MODULES:
                    return False, f"Dangerous import: {node.module}"
        
        # Check function calls
        if isinstance(node, ast.Call):
            func = node.func
            
            # Direct function calls like eval(), exec()
            if isinstance(func, ast.Name):
                if func.id in DANGEROUS_NAMES:
                    return False, f"Disallowed function call: {func.id}()"
            
            # Attribute calls like os.system(), subprocess.call()
            if isinstance(func, ast.Attribute):
                if func.attr in DANGEROUS_NAMES:
                    return False, f"Disallowed method call: .{func.attr}()"
                
                # Check if accessing dangerous module methods
                if isinstance(func.value, ast.Name):
                    if func.value.id in DANGEROUS_MODULES:
                        return False, f"Dangerous module access: {func.value.id}.{func.attr}()"
        
        # Check attribute access (e.g., os.system, df.__dict__)
        if isinstance(node, ast.Attribute):
            # Block dunder attributes
            if node.attr.startswith("__") and node.attr.endswith("__"):
                return False, f"Disallowed dunder attribute: {node.attr}"
            
            # Block access to dangerous modules
            if isinstance(node.value, ast.Name):
                if node.value.id in DANGEROUS_MODULES:
                    return False, f"Dangerous module attribute access: {node.value.id}.{node.attr}"
        
        # Check name references (block direct access to dangerous modules)
        if isinstance(node, ast.Name):
            if node.id in DANGEROUS_MODULES:
                # Allow if it's part of an import statement (already checked above)
                # This catches standalone references like: x = os
                parent_is_import = False
                # Note: This is a simplified check; in production, walk parent nodes
                if node.id in ["os", "sys", "subprocess", "socket"]:
                    logger.warning(f"Suspicious name reference: {node.id}")
                    # We'll allow this through if it's pandas 'os' (rare false positive)
                    # but log it for review
    
    # Code passed all checks
    return True, "Code is safe"


def validate_code_structure(code: str) -> Tuple[bool, str]:
    """
    Additional structural validation
    
    Checks:
    - Code has at least some statements
    - Not just comments
    - Has expected output operations (to_csv, savefig)
    
    Args:
        code: Python code string
    
    Returns:
        Tuple of (is_valid: bool, reason: str)
    """
    try:
        tree = ast.parse(code)
    except Exception as e:
        return False, f"Invalid code structure: {e}"
    
    # Count actual statements (not just comments)
    statements = [node for node in ast.walk(tree) if isinstance(node, ast.stmt)]
    
    if len(statements) < 2:
        return False, "Code too short or empty"
    
    # Check if code has output operations (at least saves results)
    code_lower = code.lower()
    has_output = any(op in code_lower for op in ["to_csv", "savefig", "print"])
    
    if not has_output:
        logger.warning("Code has no obvious output operations (to_csv, savefig, print)")
        # Don't fail, just warn
    
    return True, "Structure valid"


def quick_safety_check(code: str) -> Tuple[bool, str]:
    """
    Quick string-based safety check (supplement to AST)
    
    Args:
        code: Python code string
    
    Returns:
        Tuple of (is_safe: bool, reason: str)
    """
    code_lower = code.lower()
    
    # Check for dangerous patterns in strings
    dangerous_patterns = [
        ("subprocess", "subprocess module usage"),
        ("os.system", "os.system call"),
        ("eval(", "eval() call"),
        ("exec(", "exec() call"),
        ("__import__", "__import__ usage"),
        ("open(", "file open() call"),
        ("socket", "socket usage"),
        ("urllib", "urllib usage"),
        ("requests", "requests library usage"),
    ]
    
    for pattern, reason in dangerous_patterns:
        if pattern in code_lower:
            logger.warning(f"Potentially dangerous pattern found: {reason}")
            # Return False only for the most dangerous ones
            if pattern in ["subprocess", "os.system", "eval(", "exec("]:
                return False, f"Dangerous pattern detected: {reason}"
    
    return True, "Quick check passed"


def full_validation(code: str) -> Tuple[bool, str]:
    """
    Run all validation checks
    
    Args:
        code: Python code string
    
    Returns:
        Tuple of (is_safe: bool, reason: str)
    """
    # AST-based safety check
    is_safe, reason = is_safe_pandas(code)
    if not is_safe:
        return False, f"Safety check failed: {reason}"
    
    # Structure validation
    is_valid, reason = validate_code_structure(code)
    if not is_valid:
        return False, f"Structure validation failed: {reason}"
    
    # Quick string check
    is_safe, reason = quick_safety_check(code)
    if not is_safe:
        return False, f"Pattern check failed: {reason}"
    
    return True, "All validations passed"
