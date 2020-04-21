#!/bin/bash

#
# A utility script for pulling new changes from the GitHub
# repository and restarting the application.
#
# If you get a spawn error and added entries to requirements.pip,
#    1. Enter the virtual environment: $ source venv/bin/activate
#    2. Install the new packages:      $ pip3 install -r requirements.pip
#
# If you did not change requirements.pip, check the supervisor logs
# at /var/log/supervisor/supervisord.log or the application error
# log at: /var/log/supervisor/labhoursqueue-stderr---supervisor-etAIMv.log
#

whiptail --title "Update Lab Hours Queue" --msgbox "This utility will pull the git repository and restart the flask application." 8 78
if [ $? -eq 255 ]; then
	exit
fi

# Pull from GitHub remote
git pull

if (whiptail --title "Update Lab Hours Queue" --yesno "The repository is now up to date. Would you like to restart the web app for changes to take effect?\n\
	WARNING: This will result in the current queue being cleared!" 8 78); then
	# Restart application
	supervisorctl stop labhoursqueue
	supervisorctl start labhoursqueue
	if [ $? -eq 0 ]; then
		whiptail --title "Update Lab Hours Queue" --msgbox "The application was successfully restarted. The website is live." 8 78
	else
		whiptail --title "Update Lab Hours Queue" --msgbox "Spawn error: Failed to restart application. Check /var/log/supervisor/supervisord.log" 8 78
	fi
else
	whiptail --title "Update Lab Hours Queue" --msgbox "The server was not restarted." 8 78
fi
