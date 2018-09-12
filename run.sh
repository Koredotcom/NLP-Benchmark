#!/bin/bash

rm -rf venv/
virtualenv --python=python3 venv/
. venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt

python getParams.py
if [ $? -eq 0 ]
then
	python createIntent.py
fi
if [ $? -eq 0 ]
then
	python runTest.py testconfig.json
fi
