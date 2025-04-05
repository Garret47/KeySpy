# KeySpy - Keystroke Monitoring Simulation (Educational Purpose)

## 1. Install the required libraries

### Dependencies
You'll need to install several development libraries. Below is an example for Ubuntu:
```bash
sudo apt update
sudo apt install libcurl4-openssl-dev libxkbcommon-dev libxkbcommon-x11-dev libx11-dev libx11-xcb-dev gcc make python3 python3-venv
```

*For other systems, you'll need equivalent packages for libcurl, libxkbcommon (with X11 support), libX11, and standard build tools.*

## 2. Server Setup (Python)
### Install Python dependencies
Navigate to the app_server directory and install the required Python dependencies using pip:
```bash
python -m venv venv
source ./venv/bin/activate
cd app_server
pip install -r requirements.txt
```

## 3. Configure environment variables

Before running the server, you need to update the .env_example file with your own configuration.
After updating the values, rename the file from .env_example to .env:
```bash
nano .env_example  # Open the file for editing
mv .env_example .env
```


## 3. Run the Python Server
### Start server
You can start the server with:
```bash
python main.py
```