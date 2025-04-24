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

## 3. Configure the application
### Configuration file
The application uses a configuration file named key_spy.conf.
Copy the example file and update it with your settings.
```bash
cp key_spy.conf.example key_spy.conf
nano key_spy.conf  # Open the file for editing
```
### Environment variables (optional)
You can also create an .env file to store sensitive data like passwords and usernames:
```bash
touch .env
nano .env  # Open the file for editing
```
Add the following credentials to the .env file:
```
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_password
```
These credentials will be automatically filled in the input fields when creating a client.
## 3. Run the Python Server
### Start server
You can start the server with:
```bash
python main.py
```