"""
Sandboxed code execution with Docker and resource limits
"""
import os
import subprocess
import tempfile
import logging
import shutil
from pathlib import Path
from typing import Dict, Any

# Import resource only on Unix-like systems (not available on Windows)
try:
    import resource
    import signal
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False
    logger = logging.getLogger(__name__)
    logger.warning("resource module not available (Windows). Docker sandbox or basic fallback will be used.")

logger = logging.getLogger(__name__)

# Sandbox configuration from environment
SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "ada-sandbox:latest")
SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "120"))  # Increased to 120 seconds
USE_DOCKER = os.getenv("USE_DOCKER_SANDBOX", "true").lower() == "true"


def run_code_in_sandbox(code: str, dataset_path: str, task_id: str) -> Dict[str, Any]:
    """
    Execute Python code in an isolated sandbox environment
    
    Args:
        code: Python code to execute (already validated)
        dataset_path: Path to dataset CSV file
        task_id: Task identifier for storing outputs
    
    Returns:
        Dictionary with execution results:
        {
            'success': bool,
            'stdout': str,
            'stderr': str,
            'output_files': list,
            'error': str (if failed)
        }
    """
    if USE_DOCKER:
        try:
            return run_code_in_docker(code, dataset_path, task_id)
        except Exception as e:
            logger.error(f"Docker execution failed: {e}")
            logger.info("Falling back to rlimit-based execution (LESS SECURE)")
            return run_code_with_rlimit(code, dataset_path, task_id)
    else:
        logger.warning("Docker sandbox disabled - using rlimit fallback")
        return run_code_with_rlimit(code, dataset_path, task_id)


def run_code_in_docker(code: str, dataset_path: str, task_id: str) -> Dict[str, Any]:
    """
    Execute code in Docker container with full isolation
    
    Security features:
    - No network access (--network none)
    - Memory limit (256MB)
    - CPU limit (0.5 cores)
    - Read-only dataset mount
    - Separate output directory
    - Timeout enforcement
    
    Args:
        code: Python code to execute
        dataset_path: Path to dataset
        task_id: Task identifier
    
    Returns:
        Execution results dictionary
    """
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        script_dir = temp_path / "scripts"
        output_dir = temp_path / "outputs"
        script_dir.mkdir()
        output_dir.mkdir()
        
        # Prepare script with dataset loading
        # Inside Docker, dataset will be mounted at /data/dataset.csv
        script_content = f"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Load dataset (mounted in Docker at /data/dataset.csv)
df = pd.read_csv('/data/dataset.csv')

# Execute generated code
{code}
"""
        
        script_path = script_dir / "execute.py"
        with open(script_path, "w") as f:
            f.write(script_content)
        
        logger.info(f"Executing code in Docker (timeout: {SANDBOX_TIMEOUT}s)")
        
        # Convert Windows paths to Docker format (for Docker Desktop on Windows)
        # E:\path\to\file -> E:/path/to/file
        def to_docker_path(path: Path) -> str:
            """Convert Windows path to Docker-compatible format (Docker Desktop on Windows)"""
            abs_path = str(path.absolute())
            # Simply replace backslashes with forward slashes
            # Docker Desktop on Windows handles the drive letter automatically
            docker_path = abs_path.replace('\\', '/')
            return docker_path
        
        script_dir_docker = to_docker_path(script_dir)
        dataset_path_docker = to_docker_path(Path(dataset_path))
        output_dir_docker = to_docker_path(output_dir)
        
        # Construct Docker command
        cmd = [
            "docker", "run",
            "--rm",  # Remove container after execution
            "--init",  # Use init process to handle signals properly
            "--network", "none",  # No network access
            "--memory", "512m",  # 512MB memory limit (increased for pandas/matplotlib)
            "--cpus", "1.0",  # 1.0 CPU limit (increased)
            "-v", f"{script_dir_docker}:/scripts:ro",  # Read-only scripts
            "-v", f"{dataset_path_docker}:/data/dataset.csv:ro",  # Read-only dataset
            "-v", f"{output_dir_docker}:/tmp:rw",  # Writable output dir
            SANDBOX_IMAGE,
            "python", "/scripts/execute.py"
        ]
        
        logger.info(f"Docker command: {' '.join(cmd)}")
        logger.info(f"Script directory (Docker): {script_dir_docker}")
        logger.info(f"Dataset path (Docker): {dataset_path_docker}")
        logger.info(f"Output directory (Docker): {output_dir_docker}")
        
        try:
            # Execute with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=SANDBOX_TIMEOUT
            )
            
            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode
            
            logger.info(f"Docker exit code: {returncode}")
            if stdout:
                logger.info(f"Docker stdout: {stdout[:500]}")
            if stderr:
                logger.info(f"Docker stderr: {stderr[:500]}")
            
            # Copy output files to task directory
            from .utils import get_data_dirs
            dirs = get_data_dirs()
            task_output_dir = dirs["tasks"] / task_id / "outputs"
            task_output_dir.mkdir(parents=True, exist_ok=True)
            
            output_files = []
            for output_file in output_dir.iterdir():
                if output_file.is_file():
                    dest = task_output_dir / output_file.name
                    shutil.copy2(output_file, dest)
                    output_files.append(output_file.name)
                    logger.info(f"Copied output file: {output_file.name}")
            
            if returncode == 0:
                logger.info("Code executed successfully in Docker")
                return {
                    'success': True,
                    'stdout': stdout,
                    'stderr': stderr,
                    'output_files': output_files
                }
            else:
                logger.error(f"Docker execution failed with code {returncode}")
                return {
                    'success': False,
                    'stdout': stdout,
                    'stderr': stderr,
                    'output_files': output_files,
                    'error': f"Execution failed with exit code {returncode}"
                }
        
        except subprocess.TimeoutExpired:
            logger.error(f"Docker execution timeout after {SANDBOX_TIMEOUT}s")
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution timeout after {SANDBOX_TIMEOUT} seconds',
                'output_files': [],
                'error': 'Timeout'
            }
        
        except FileNotFoundError:
            logger.error("Docker not found - ensure Docker is installed and in PATH")
            raise RuntimeError("Docker not available")
        
        except Exception as e:
            logger.error(f"Docker execution error: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'output_files': [],
                'error': f"Docker error: {e}"
            }


def run_code_with_rlimit(code: str, dataset_path: str, task_id: str) -> Dict[str, Any]:
    """
    Execute code with resource limits (fallback for when Docker unavailable)
    
    ⚠️ WARNING: This is LESS SECURE than Docker isolation!
    Only for local development. DO NOT use in production.
    
    Uses Python resource module to set:
    - CPU time limit
    - Memory limit
    - File size limit
    
    Args:
        code: Python code to execute
        dataset_path: Path to dataset
        task_id: Task identifier
    
    Returns:
        Execution results dictionary
    """
    logger.warning("⚠️ Using rlimit fallback - NOT as secure as Docker!")
    
    from .utils import get_data_dirs
    dirs = get_data_dirs()
    task_output_dir = dirs["tasks"] / task_id / "outputs"
    task_output_dir.mkdir(parents=True, exist_ok=True)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "execute.py"
        
        # Prepare script
        script_content = f"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os

# Change working directory to output dir
os.chdir(r'{task_output_dir.absolute()}')

# Replace /tmp with actual output directory
import builtins
original_open = builtins.open

def safe_open(file, *args, **kwargs):
    # Redirect /tmp paths to output directory
    if isinstance(file, str) and file.startswith('/tmp/'):
        file = r'{task_output_dir.absolute()}' + '/' + file[5:]
    return original_open(file, *args, **kwargs)

builtins.open = safe_open

# Load dataset
df = pd.read_csv(r'{dataset_path}')

# Execute generated code
{code}
"""
        
        with open(script_path, "w") as f:
            f.write(script_content)
        
        def set_limits():
            """Set resource limits in child process (Unix-like systems only)"""
            if not HAS_RESOURCE:
                logger.warning("resource module not available - cannot set rlimits (Windows system)")
                return
            
            try:
                # CPU time limit (seconds)
                resource.setrlimit(resource.RLIMIT_CPU, (SANDBOX_TIMEOUT, SANDBOX_TIMEOUT))
                
                # Memory limit (default 1024MB; configurable)
                mem_limit_mb = int(os.getenv("SANDBOX_RLIMIT_AS_MB", "1024"))
                mem_limit = mem_limit_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
                
                # File size limit (50MB)
                file_limit = 50 * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
                
            except Exception as e:
                logger.warning(f"Could not set resource limits: {e}")
        
        try:
            # Prevent numpy/OpenBLAS from trying to spawn many threads in constrained environments
            child_env = dict(os.environ)
            child_env.setdefault("OMP_NUM_THREADS", "1")
            child_env.setdefault("OPENBLAS_NUM_THREADS", "1")
            child_env.setdefault("MKL_NUM_THREADS", "1")
            child_env.setdefault("NUMEXPR_NUM_THREADS", "1")
            child_env.setdefault("VECLIB_MAXIMUM_THREADS", "1")
            child_env.setdefault("BLIS_NUM_THREADS", "1")

            # Execute with limits (Unix-like systems only)
            result = subprocess.run(
                ["python", str(script_path)],
                capture_output=True,
                text=True,
                timeout=SANDBOX_TIMEOUT + 5,  # Add buffer to timeout
                env=child_env,
                preexec_fn=set_limits if os.name != 'nt' else None  # Linux/Mac only
            )
            
            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode
            
            # List output files
            output_files = [f.name for f in task_output_dir.iterdir() if f.is_file()]
            
            if returncode == 0:
                logger.info("Code executed successfully with rlimit")
                return {
                    'success': True,
                    'stdout': stdout,
                    'stderr': stderr,
                    'output_files': output_files
                }
            else:
                logger.error(f"rlimit execution failed with code {returncode}")
                return {
                    'success': False,
                    'stdout': stdout,
                    'stderr': stderr,
                    'output_files': output_files,
                    'error': f"Execution failed with exit code {returncode}"
                }
        
        except subprocess.TimeoutExpired:
            logger.error("rlimit execution timeout")
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution timeout after {SANDBOX_TIMEOUT} seconds',
                'output_files': [],
                'error': 'Timeout'
            }
        
        except Exception as e:
            logger.error(f"rlimit execution error: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'output_files': [],
                'error': str(e)
            }


def check_docker_available() -> bool:
    """
    Check if Docker is available and sandbox image exists
    
    Returns:
        True if Docker is ready, False otherwise
    """
    try:
        # Check if docker command exists
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            return False
        
        # Check if sandbox image exists
        result = subprocess.run(
            ["docker", "images", "-q", SANDBOX_IMAGE],
            capture_output=True,
            timeout=5
        )
        
        if not result.stdout.strip():
            logger.warning(f"Sandbox image '{SANDBOX_IMAGE}' not found")
            logger.info("Build it with: docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/")
            return False
        
        return True
    
    except FileNotFoundError:
        logger.warning("Docker command not found")
        return False
    except Exception as e:
        logger.error(f"Error checking Docker availability: {e}")
        return False
