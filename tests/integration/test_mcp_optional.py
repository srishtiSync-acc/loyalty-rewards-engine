import os
import subprocess
import sys


def test_core_package_imports_without_mcp_dependency():
    source = """
import builtins
real_import = builtins.__import__
def blocked_import(name, *args, **kwargs):
    if name == 'mcp' or name.startswith('mcp.'):
        raise ImportError('MCP intentionally unavailable')
    return real_import(name, *args, **kwargs)
builtins.__import__ = blocked_import
import loyalty_rewards
assert loyalty_rewards.LoyaltyEngine
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.path.abspath("src")
    result = subprocess.run([sys.executable, "-c", source], env=environment, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
