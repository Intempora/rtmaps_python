#!/bin/bash


python -m venv .venv-rtmaps
source .venv-rtmaps/Scripts/activate

pip install -i https://test.pypi.org/simple/ rtmaps==0.0.2
pip install -r requierements.txt

