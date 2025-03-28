# KeySpy - Keystroke Monitoring Simulation (Educational Purpose)

## 1. Install the required libraries

### On Debian-based systems (like Ubuntu)
To install the necessary dependencies on Debian-based systems (such as Ubuntu), run the following commands:

```bash
sudo apt update
sudo apt install libcurl4-openssl-dev libxkbcommon-dev libxkbcommon-x11-dev libx11-dev libx11-xcb-dev gcc makeems (like Fedora):
```
### On Red Hat-based systems (like Fedora)
For Red Hat-based systems (such as Fedora), use these commands:
```bash
sudo dnf update
sudo dnf install libcurl-devel xkbcommon-devel xkbcommon-x11-devel libX11-devel libX11-xcb-devel gcc make
```

## 2. Server Setup (Python)
### Install Python dependencies
Navigate to the app_server directory and install the required Python dependencies using pip:
```bash
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