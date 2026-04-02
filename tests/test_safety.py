"""
Unit tests for safety validator
"""
import pytest
from backend.app.safety import is_safe_pandas, full_validation


class TestSafePandas:
    """Test cases for is_safe_pandas validator"""
    
    def test_safe_pandas_code(self):
        """Test that safe pandas code passes validation"""
        safe_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_grouped = df.groupby('category')['sales'].sum()
df_grouped.to_csv('/tmp/result.csv', index=False)

plt.figure()
plt.bar(df_grouped.index, df_grouped.values)
plt.savefig('/tmp/plot1.png')
print('Analysis complete')
"""
        is_safe, reason = is_safe_pandas(safe_code)
        assert is_safe, f"Safe code rejected: {reason}"
        assert reason == "Code is safe"
    
    def test_reject_eval(self):
        """Test that eval() is rejected"""
        unsafe_code = """
import pandas as pd
result = eval('malicious code')
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "eval" in reason.lower()
    
    def test_reject_exec(self):
        """Test that exec() is rejected"""
        unsafe_code = """
import pandas as pd
exec('malicious code')
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "exec" in reason.lower()
    
    def test_reject_open(self):
        """Test that open() is rejected"""
        unsafe_code = """
import pandas as pd
with open('/etc/passwd', 'r') as f:
    data = f.read()
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "open" in reason.lower()
    
    def test_reject_os_import(self):
        """Test that os module import is rejected"""
        unsafe_code = """
import pandas as pd
import os
os.system('ls')
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "os" in reason.lower()
    
    def test_reject_subprocess(self):
        """Test that subprocess import is rejected"""
        unsafe_code = """
import pandas as pd
import subprocess
subprocess.call(['ls', '-la'])
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "subprocess" in reason.lower()
    
    def test_reject_socket(self):
        """Test that socket import is rejected"""
        unsafe_code = """
import pandas as pd
import socket
s = socket.socket()
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "socket" in reason.lower()
    
    def test_reject_import_from_os(self):
        """Test that 'from os import' is rejected"""
        unsafe_code = """
import pandas as pd
from os import system
system('whoami')
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "os" in reason.lower()
    
    def test_reject_dunder_globals(self):
        """Test that __globals__ access is rejected"""
        unsafe_code = """
import pandas as pd
x = df.__globals__
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "__globals__" in reason.lower() or "dunder" in reason.lower()
    
    def test_reject_dunder_dict(self):
        """Test that __dict__ access is rejected"""
        unsafe_code = """
import pandas as pd
x = df.__dict__
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "__dict__" in reason.lower() or "dunder" in reason.lower()
    
    def test_reject_getattr(self):
        """Test that getattr is rejected"""
        unsafe_code = """
import pandas as pd
func = getattr(df, 'some_method')
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "getattr" in reason.lower()
    
    def test_reject_compile(self):
        """Test that compile() is rejected"""
        unsafe_code = """
import pandas as pd
code = compile('print(1)', '<string>', 'exec')
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "compile" in reason.lower()
    
    def test_reject_import(self):
        """Test that __import__ is rejected"""
        unsafe_code = """
import pandas as pd
os = __import__('os')
os.system('ls')
"""
        is_safe, reason = is_safe_pandas(unsafe_code)
        assert not is_safe
        assert "import" in reason.lower()
    
    def test_syntax_error_handling(self):
        """Test that syntax errors are caught"""
        invalid_code = """
import pandas as pd
this is not valid python
"""
        is_safe, reason = is_safe_pandas(invalid_code)
        assert not is_safe
        assert "syntax" in reason.lower() or "parse" in reason.lower()
    
    def test_allowed_numpy(self):
        """Test that numpy is allowed"""
        safe_code = """
import pandas as pd
import numpy as np
arr = np.array([1, 2, 3])
mean = np.mean(arr)
"""
        is_safe, reason = is_safe_pandas(safe_code)
        assert is_safe, f"Numpy code rejected: {reason}"
    
    def test_allowed_matplotlib(self):
        """Test that matplotlib is allowed"""
        safe_code = """
import pandas as pd
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
plt.savefig('/tmp/plot.png')
"""
        is_safe, reason = is_safe_pandas(safe_code)
        assert is_safe, f"Matplotlib code rejected: {reason}"
    
    def test_complex_safe_code(self):
        """Test complex but safe pandas operations"""
        safe_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Data processing
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df_filtered = df[df['sales'] > 0]
grouped = df_filtered.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'quantity': 'sum'
})

# Save results
grouped.to_csv('/tmp/result.csv')

# Visualization
fig, axes = plt.subplots(2, 1, figsize=(10, 8))
axes[0].bar(grouped.index, grouped['sales']['sum'])
axes[1].plot(grouped.index, grouped['sales']['mean'], marker='o')
plt.tight_layout()
plt.savefig('/tmp/plot1.png')

print(f'Processed {len(df_filtered)} rows')
"""
        is_safe, reason = is_safe_pandas(safe_code)
        assert is_safe, f"Complex safe code rejected: {reason}"


class TestFullValidation:
    """Test full validation pipeline"""
    
    def test_empty_code(self):
        """Test that empty code is rejected"""
        is_valid, reason = full_validation("")
        assert not is_valid
        assert "empty" in reason.lower() or "short" in reason.lower()
    
    def test_only_comments(self):
        """Test that code with only comments is rejected"""
        code = """
# Just a comment
# Another comment
"""
        is_valid, reason = full_validation(code)
        assert not is_valid
    
    def test_complete_safe_code(self):
        """Test that complete safe code passes all validations"""
        code = """
import pandas as pd
df_result = df.head(10)
df_result.to_csv('/tmp/result.csv', index=False)
print('Done')
"""
        is_valid, reason = full_validation(code)
        assert is_valid, f"Complete safe code rejected: {reason}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
