#!/usr/bin/env python3
"""
Environment Diagnostic & Fix Script
Helps identify and resolve Python environment issues
"""

import sys
import os
import subprocess
from pathlib import Path

def print_colored(text: str, color_code: str = "0") -> None:
    """Print colored text"""
    print(f"\033[{color_code}m{text}\033[0m")

def print_header(title: str) -> None:
    """Print section header"""
    print_colored(f"\n🔍 {title}", "96")  # Cyan
    print_colored("=" * 60, "94")  # Blue

def print_success(message: str) -> None:
    """Print success message"""
    print_colored(f"✅ {message}", "92")  # Green

def print_error(message: str) -> None:
    """Print error message"""
    print_colored(f"❌ {message}", "91")  # Red

def print_warning(message: str) -> None:
    """Print warning message"""
    print_colored(f"⚠️  {message}", "93")  # Yellow

def print_info(message: str) -> None:
    """Print info message"""
    print_colored(f"🔧 {message}", "97")  # White

def run_command(command: str) -> tuple:
    """Run a command and return (success, output)"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def check_python_environments():
    """Check available Python environments"""
    print_header("Python Environment Analysis")
    
    # Current Python
    print_info("Current Python Environment:")
    print_success(f"Python: {sys.version}")
    print_success(f"Executable: {sys.executable}")
    print_success(f"Path: {sys.path[0] if sys.path else 'Unknown'}")
    
    # Check conda
    print_info("\nConda Environment Check:")
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'Not detected')
    print_success(f"Conda Environment: {conda_env}")
    
    # Find conda python
    success, conda_python = run_command("which python")
    if success:
        print_success(f"Conda Python: {conda_python}")
    else:
        print_warning("Conda Python not found in PATH")
    
    # Check available pythons
    print_info("\nAvailable Python Interpreters:")
    for python_cmd in ['python', 'python3', 'python3.12', 'python3.13']:
        success, path = run_command(f"which {python_cmd}")
        if success:
            # Get version
            success_ver, version = run_command(f"{path} --version")
            if success_ver:
                print_success(f"{python_cmd}: {path} ({version})")
            else:
                print_success(f"{python_cmd}: {path}")
        else:
            print_warning(f"{python_cmd}: Not found")

def check_dependencies_in_environment(python_path: str):
    """Check dependencies in a specific Python environment"""
    print_header(f"Dependencies in {python_path}")
    
    deps_to_check = ['PyQt5', 'pydantic', 'lxml']
    
    for dep in deps_to_check:
        success, output = run_command(f"{python_path} -c 'import {dep}; print({dep}.__version__ if hasattr({dep}, \"__version__\") else \"Available\")'")
        if success:
            print_success(f"{dep}: {output}")
        else:
            print_error(f"{dep}: Not available")

def find_correct_python():
    """Find the Python interpreter with required dependencies"""
    print_header("Finding Correct Python Environment")
    
    # List of potential Python interpreters to check
    python_candidates = []
    
    # Add conda python
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env and conda_env != 'base':
        conda_python = f"conda run -n {conda_env} python"
        python_candidates.append(("Conda Environment", conda_python))
    
    # Add common Python paths
    common_pythons = [
        ("Current Python", sys.executable),
        ("System Python", "python"),
        ("System Python3", "python3"),
    ]
    
    for name, cmd in common_pythons:
        success, path = run_command(f"which {cmd}" if not path.startswith('/') else f"echo {cmd}")
        if success:
            python_candidates.append((name, path if path.startswith('/') else cmd))
    
    # Check each candidate
    working_pythons = []
    for name, python_cmd in python_candidates:
        print_info(f"\nChecking {name}: {python_cmd}")
        
        # Test basic import
        success, _ = run_command(f"{python_cmd} -c 'import sys; print(sys.version)'")
        if not success:
            print_warning(f"Cannot execute {python_cmd}")
            continue
        
        # Check dependencies
        deps_available = 0
        for dep in ['PyQt5', 'pydantic', 'lxml']:
            success, _ = run_command(f"{python_cmd} -c 'import {dep}'")
            if success:
                deps_available += 1
        
        if deps_available == 3:
            print_success(f"✅ All dependencies available in {name}")
            working_pythons.append((name, python_cmd, deps_available))
        elif deps_available > 0:
            print_warning(f"⚠️  {deps_available}/3 dependencies in {name}")
            working_pythons.append((name, python_cmd, deps_available))
        else:
            print_error(f"❌ No dependencies in {name}")
    
    return working_pythons

def create_validation_runner(python_cmd: str):
    """Create a script to run validation with the correct Python"""
    script_content = f'''#!/bin/bash
# Auto-generated validation runner
echo "🚀 Running Day 3 validation with correct Python environment..."
echo "Python: {python_cmd}"
echo "Current directory: $(pwd)"
echo "=================================================="

{python_cmd} src/validate_day3_improved.py
'''
    
    runner_path = Path.cwd() / "run_validation.sh"
    try:
        with open(runner_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(runner_path, 0o755)
        print_success(f"Created validation runner: {runner_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create runner: {e}")
        return False

def install_missing_dependencies(python_cmd: str):
    """Install missing dependencies"""
    print_header("Installing Missing Dependencies")
    
    # Determine pip command
    pip_cmd = python_cmd.replace('python', 'pip')
    
    dependencies = ['PyQt5', 'pydantic', 'lxml']
    
    print_info(f"Installing with: {pip_cmd}")
    
    for dep in dependencies:
        print_info(f"Installing {dep}...")
        success, output = run_command(f"{pip_cmd} install {dep}")
        if success:
            print_success(f"{dep} installed successfully")
        else:
            print_warning(f"Failed to install {dep}: {output}")

def main():
    """Main diagnostic function"""
    print_colored("🔍 ARXML Viewer Pro - Environment Diagnostic", "1")  # Bold
    print_colored("=" * 60, "94")
    
    # Step 1: Analyze current environment
    check_python_environments()
    
    # Step 2: Check dependencies in current environment
    check_dependencies_in_environment(sys.executable)
    
    # Step 3: Find working Python environment
    working_pythons = find_correct_python()
    
    if not working_pythons:
        print_header("No Working Python Found - Installing Dependencies")
        install_missing_dependencies(sys.executable)
        # Re-check after installation
        working_pythons = find_correct_python()
    
    if working_pythons:
        # Sort by number of available dependencies (descending)
        working_pythons.sort(key=lambda x: x[2], reverse=True)
        best_python = working_pythons[0]
        
        print_header("Recommended Solution")
        print_success(f"Best Python environment: {best_python[0]}")
        print_success(f"Command: {best_python[1]}")
        print_success(f"Dependencies: {best_python[2]}/3 available")
        
        # Create runner script
        if create_validation_runner(best_python[1]):
            print_header("Next Steps")
            print_info("To run the Day 3 validation:")
            print_colored("./run_validation.sh", "93")  # Yellow
            print_info("\nOr run directly:")
            print_colored(f"{best_python[1]} src/validate_day3_improved.py", "93")
        
        # If conda environment, provide conda-specific advice
        if 'conda' in best_python[1].lower() or os.environ.get('CONDA_DEFAULT_ENV'):
            print_header("Conda Environment Tips")
            print_info("If using conda, ensure you're in the correct environment:")
            print_colored("conda activate base  # or your environment name", "93")
            print_colored("python src/validate_day3_improved.py", "93")
    
    else:
        print_header("No Working Environment Found")
        print_error("Unable to find a Python environment with all required dependencies")
        print_info("Please install the dependencies manually:")
        print_colored("pip install PyQt5 pydantic lxml", "93")

if __name__ == "__main__":
    main()