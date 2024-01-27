#!/usr/bin/env python

# DDNS-NG, a modular Dynamic DNS updater
# Copyright (C) 2019 Heiko Rothkranz
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Requires:
# ipy - https://github.com/autocracy/python-ipy/

import os
import sys
import configparser
import importlib
from IPy import IP

# 0 - Read the config file and initialise

# Determine config file path
if len(sys.argv) > 1:
	# A command line argument was given -> try using it as config file
	config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), sys.argv[1])
else:
	# No command line argument -> use default config file path
	config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini")

# Check if the config file exists
if not os.path.isfile(config_file):
	sys.exit("Could not find the configuration file. Provide a path to the config file as a command line argument or call the script without any arguments.")

# Read config file
config = configparser.ConfigParser()
try:
	config.read(config_file) # TODO: throw exception if invalid config file?
except:
	sys.exit("Configuration file exists but could not be read.")

# import modules based on configuration file
prechecks = []
modules = config.get('MODULES', 'prechecker').split(',')
for module in modules:
	prechecks.append(importlib.import_module('.' + module.strip(), 'precheckers'))
ipretrievers = []
modules = config.get('MODULES', 'ipretriever').split(',')
for module in modules:
	ipretrievers.append(importlib.import_module('.' + module.strip(), 'ipretrievers'))
oldips = []
modules = config.get('MODULES', 'oldipchecker').split(',')
for module in modules:
	oldips.append(importlib.import_module('.' + module.strip(), 'oldipcheckers'))
dnss = []
modules = config.get('MODULES', 'dnsupdater').split(',')
for module in modules:
	dnss.append(importlib.import_module('.' + module.strip(), 'dnsupdaters'))

# 1 - Optional: Figure out if we need to run an update at all, i.e. by checking for a ressource on a webserver on the old IP. Exit if the following functions return False.

cont = False
for precheck in prechecks:
	if precheck.needUpdate():
		cont = True
		break
if not cont:
	# All pre-checks succeeded, i.e. we do not need to run the script any further
	if not config.getboolean('DEFAULT', 'quiet'):
		print("INFO: Pre-checks successful: No update required.")
	sys.exit()

# 2 - Retrieve public IP addresses

new_ipv4 = None
new_ipv6 = None
for ipretriever in ipretrievers:
	new_ip = IP(ipretriever.getIP())
	if new_ip.version() == 4:
		new_ipv4 = new_ip
		if not config.getboolean('DEFAULT', 'quiet'):
			print(f"INFO: Your external IPv4 address: {new_ipv4.strNormal()}")
	if new_ip.version() == 6:
		new_ipv6 = new_ip
		if not config.getboolean('DEFAULT', 'quiet'):
			print(f"INFO: Your external IPv6 address: {new_ipv6.strNormal()}")
	if new_ipv4 and new_ipv6:
		# retrieved both IPv4 and IPv6 addresses -> stop trying to retrieve more addresses and continue the update
		break
if not new_ipv4 and not config.getboolean('DEFAULT', 'quiet'):
	print("INFO: Could not retrieve IPv4 address. Please check whether your module for retrieving your external IPv4 works correctly, or choose another one.")
if not new_ipv6 and not config.getboolean('DEFAULT', 'quiet'):
	print("INFO: Could not retrieve IPv6 address. Please check whether your module for retrieving your external IPv4 works correctly, or choose another one.")
if not new_ipv4 and not new_ipv6:
	sys.exit("ERROR: Could not retrieve any IP address. Please check whether your modules for retrieveing your external IP addresses work correctly, or choose other ones.")

# 3 - Optional: Check if the IP addresses changed since the last update. Do not update when the following functions return False.

ipv4_changed = False
ipv6_changed = False
for oldip in oldips:
	if new_ipv4 and oldip.changedIPv4(new_ipv4):
		# IPv4 address changed since last update.
		ipv4_changed = True
	if new_ipv6 and oldip.changedIPv6(new_ipv6):
		# IPv6 address changed since last update.
		ipv6_changed = True

if not ipv4_changed and not ipv6_changed:
	# Both IPv4 and IPv6 addresses didn't change. Exit.
	if not config.getboolean('DEFAULT', 'quiet'):
		print("INFO: IP addresses unchanged. Nothing to update.")
	sys.exit()

# 4 - Update DNS

for dns in dnss:
	# pass new IP addresses or None to the DNS update scripts
	dns.update(new_ipv4, new_ipv6)

# 5 - Optional: Write new IP addresses into storage

for oldip in oldips:
	oldip.save(new_ipv4, new_ipv6)

