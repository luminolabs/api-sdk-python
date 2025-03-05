#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if twine is installed, if not, install it
if ! command -v twine &> /dev/null; then
    echo "twine not found, please install it with 'pip install twine'"
    exit
fi

# Check if a ~/.pypirc file exists, if not, error out
if [ ! -f ~/.pypirc ]; then
    echo "Please create a ~/.pypirc file with your PyPI API token; example:"
    echo "Example:"
    echo "[distutils]"
    echo "  index-servers ="
    echo "    lumino"
    echo ""
    echo "[lumino]"
    echo "  repository = https://upload.pypi.org/legacy/"
    echo "  username = __token__"
    echo "  password = pypi-......"
    exit
fi

# Remove any old distributions
echo "Removing old distributions..."
rm -rf dist/*

# Create source distribution and wheel
echo "Building the package..."
python setup.py sdist bdist_wheel

# Upload the package to PyPI
echo "Uploading the package to PyPI..."
twine upload --repository lumino-api-sdk-python dist/*

# Clean up
echo "Cleaning up build files..."
rm -rf build dist *.egg-info

echo "Package successfully uploaded to PyPI!"