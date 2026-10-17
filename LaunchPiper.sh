#!/usr/bin/bash

export PIPER_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $PIPER_ROOT/.venv/bin/activate
echo "Python path: $(which python)"
echo "Launching Piper"
python LaunchPiper.py