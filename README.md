# HomeGuard

HomeGuard is a tool that allows you to map devices on your network and recieve alerts when a device is active in a certain time and date range. This app can be run on any computer or installed on a server or Raspberry Pi to run all day. This document describes how to set up the application on a Raspberry Pi as well as how to use it.

# Summary

- [Raspberry Pi Setup](#raspberry-pi-setup)
- [Dependencies](#dependencies)
    - [Ubuntu Server](#ubuntu-server-use-if-following-raspberry-pi-configuration)
    - [Environments with pip](#environments-with-pip)
- [Running](#running)
- [Installing](#installing)
- [Usage](#usage)
    - [Status Section](#status-section)
    - [Event Section](#event-section)
    - [Device Section](#device-section)

# Raspberry Pi Setup

First install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on the official website and insert your Raspberry Pi's SD card in your computer.

Open the Raspberry Pi Imager app and follow the following steps:

- Select the 'Choose OS' button
- Select 'Other general-purpose OS' > 'Ubuntu'
- Choose Ubuntu Server 23.04 (32 or 64 bits version depending on your Raspberry Pi)
 
Open the settings by selecting the icon at the bottom right corner

- Enable 'Set hostname' and type in 'homeguard'
- Enable 'Enable SSH' and 'Password authentication'
    - Enable 'Set username and password' and use the values of your choice
- Enable 'Configure wireless LAN'
    - Fill in your wi-fi SSID and password (The app auto-fills the current network credentials)
    - Select your country in 'Wireless LAN country'
- Enable 'Set locale settings' and select your time zone and keyboard layout
- Select 'Save' and close the settings window

Select 'Choose storage' and select your Raspberry Pi's SD card

Select 'Write' and go grab a coffee.

Once the process is done, put the SD card back in the Raspberry Pi.

Turn your Raspberry Pi on. If you've done everything correctly, it should automatically connect to your network.

Open your router's control panel and check the IP address assigned to the device. If it does not show up in the device list, waiting a few minutes or plug it directly to your router via ethernet.

Once you identified the IP address, connect through SSH using the previously set up credentials:

```sh
ssh <user>@<ip_address>
```
Update your system by using:
```sh
sudo apt update && sudo apt upgrade -y
```

# Dependencies:

First check your python version. The app requires Python version 3.10 or greater.
```sh
python3 --version
```
If your python version is older than 3.10, you will need install a newer version manually.

Now, install the required python packages to run the app:

## Ubuntu Server (use if following Raspberry Pi configuration)
Ubuntu server environments do not come with pip installed by default and packages should be installed through apt. Use the following command to install all dependencies:
```sh
sudo apt install python3-flask python3-waitress python3-requests python3-schedule python3-dotenv python3-scapy python3-netaddr python3-netifaces python3-discord -y
```

## Environments with pip
If pip is available on your platform, use the following commands to install all dependencies:

```sh
pip3 install flask waitress requests schedule python-dotenv scapy netaddr netifaces discord
```

Finally, clone the project using:
```sh
git clone https://github.com/Shsl4/HomeGuard
cd HomeGuard
```

# Running

This app can be run locally on macOS and Windows and Linux but requires admin privileges.

### Windows (admin prompt will show up automatically)
```sh
python3 main.py
```

### macOS / Linux
```sh
sudo python3 main.py
```

# Installing

This app can only be installed on Linux. You can install the app using:
```sh
sudo ./install.sh
```

The install script copies the repsitory to /opt/HomeGuard and sets up a daemon that will run the program on startup. The program data will be stored stored inside /var/lib/HomeGuard. To uninstall the app, simply use the uninstall script.

# Usage

To access the control panel, use any browser and connect to
```
<your_device_ip_address>:8080
```

The control panel is pretty straightforward to use and is split in three sections.

## Status section

The status section gives you general information about devices and events, and allows you to set up the discord webhook.

### Discord Webhook setup

In order to recieve messages on Discord, follow these simple instructions:

1. Download the [Discord](https://discord.com/) app for your platform, then log in or create and account.
2. Create a new server by pressing the '+' icon in the left navigation bar.
3. Select 'Create my own' > 'For me and my friends' and name your server.
4. Press the gear icon of the 'general' text channel.
5. Select the 'Integrations' option then press the 'Create Webhook' button
6. Click on the newly created webhook and copy the URL.
7. Open the HomeGuard control panel, paste the link and press send. You will recieve a status notification at the bottom right of the screen and a discord message if the operation succeeded.

## Event section

The event section allows you to create events that will send a message when device activity is detected.

To create a new event, press the 'Add event' button. Every interface element is detailed below:

- Event name: Used to identify an event
- Devices: Allows you to select which devices will trigger the event. Select a device in the dropdown list and press the 'Add' button to add the device. The device name will then appear in a list. Press the 'X' button next to the device name to remove it from the list
- Start Date - End Date: Selects the date range in which the event will trigger
- Start Time - End Time: Selects the time range in which the event will trigger every day
- Selected days: Selects the weekdays on which the event will trigger

Once every parameter is filled in, the 'Add' button will be enabled automatically. When the button is pressed, the creation request will be sent to the server and a success / failure message will appear in the bottom right corner of the screen.

If the operation succeeded, your event will appear in the list. You can edit the event by pressing the 'Edit button'.

Each device can trigger an event once a day. Event trigger restarts every day at midnight.

## Device section

The device section lists every device that has been recognized on the network. Devices cannot be added manually but the following information can be edited:

- Device name: A human readable name for the device
- MAC address: The identified MAC address for the device
- IP Addresses: Allows to add / remove IP addresses related to this device

There are other uneditable fields:

- Identified names: The names that HomeGuard identified for this device by analyzing traffic
- UUID: The unique id used by HomeGuard to identify the device internally
- Last Activity: The last date and time the device was seen on the network

You can also forget the device information by pressing the 'Forget' button. 
