#!/usr/bin/env bash
# UPWARDS Drone Project - one-time setup for Mac or Linux.
# Run it from a terminal in this folder:   bash setup_mac_linux.sh
# It builds a Python environment, installs everything, and checks it.
# Uses Python 3.11 or 3.12 (3.10 to 3.13 also work). Works for the simulator and for
# flying a real Tello over Wi-Fi.
set -e
cd "$(dirname "$0")"

# Find Python 3. On a Mac, the built-in may be old or missing.
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo ""
  echo "Python 3 was not found."
  echo "  Mac:   install it from https://www.python.org/downloads/  (or:  brew install python@3.12)"
  echo "  Linux: sudo apt install python3 python3-venv python3-pip"
  echo "Then run this script again."
  exit 1
fi
echo "Using this Python:"
"$PY" --version
echo ""

echo "Creating the virtual environment (.venv)..."
"$PY" -m venv .venv
VPY=".venv/bin/python"
if [ ! -x "$VPY" ]; then
  echo "The environment could not be created. On Linux you may need:  sudo apt install python3-venv"
  exit 1
fi

echo "Upgrading pip..."
"$VPY" -m pip install --upgrade pip

echo "Installing OpenCV, matplotlib, av, and pillow..."
"$VPY" -m pip install opencv-contrib-python matplotlib av pillow

echo "Installing djitellopy (with --no-deps so it does not fight OpenCV)..."
"$VPY" -m pip install --no-deps djitellopy

echo "Checking the install..."
"$VPY" check_setup.py

echo ""
echo "Setup finished. Activate it later with:  source .venv/bin/activate"
echo "Then read DRONE_HANDBOOK and run:  python example_mission.py"
