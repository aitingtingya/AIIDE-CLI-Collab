#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Callqw - Setup Script
Leader Agent 与 Qwen Code 协作桥接脚本的安装配置
"""

from setuptools import setup
from pathlib import Path

# 读取README文件
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="callqw",
    version="1.0.0",
    description="Leader Agent 与 Qwen Code 的协作桥接器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gingerman",
    author_email="",
    url="",
    py_modules=["callqw"],
    entry_points={
        "console_scripts": [
            "callqw=callqw:main",
        ],
    },
    install_requires=[
        "colorama",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="ai, qwen, bridge, assistant, code, collaboration",
    project_urls={
        "Bug Reports": "",
        "Source": "",
    },
)
