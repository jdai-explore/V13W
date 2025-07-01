#!/usr/bin/env python3
"""
ARXML Viewer Pro - Setup Configuration
Professional AUTOSAR ARXML file viewer for automotive engineers
"""

from setuptools import setup, find_packages
import os

def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "ARXML Viewer Pro - Professional AUTOSAR ARXML file viewer"

def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="arxml-viewer-pro",
    version="1.0.0",
    author="Jayadev Meka",
    author_email="jd@miraiflow.tech",
    description="Professional AUTOSAR ARXML file viewer for automotive engineers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jdai-explore/V13W",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Tools",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "black>=23.7.0",
            "mypy>=1.5.1",
            "flake8>=6.0.0",
            "PyInstaller>=5.13.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "arxml-viewer=arxml_viewer.main:main",
        ],
        "gui_scripts": [
            "arxml-viewer-gui=arxml_viewer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "arxml_viewer": [
            "resources/icons/*.png",
            "resources/icons/*.svg", 
            "resources/themes/*.qss",
            "resources/sample_data/*.arxml",
        ],
    },
    zip_safe=False,
)
