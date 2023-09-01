#! /usr/bin/env bash

# Initialize new droplet with username.
# Usage:
# $ ./init-droplet.sh new-user
#
# These commands should be run as the root user.

username=$1

adduser ${username}
sudo usermod -aG sudo docker ${username}

su ${username}

mkdir ~/.ssh
sudo cp .ssh/authorized_keys ~/.ssh
chown ${username}:${username} ~/.ssh/authorized_keys

echo "Don't forget to setup your environment variables next!"

