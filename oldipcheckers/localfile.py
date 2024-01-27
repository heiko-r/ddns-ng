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

# Basic module to save the IP addresses to a local file and to compare them on the next run

import os

IPV4_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ipv4.txt")
IPV6_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ipv6.txt")

def changedIPv4(new_ipv4):
	ipv4_filehandler = open(IPV4_FILE, 'r+')
	old_ipv4 = ipv4_filehandler.read().strip()
	ipv4_filehandler.close()
	return old_ipv4 != new_ipv4.strNormal()

def changedIPv6(new_ipv6):
	ipv6_filehandler = open(IPV6_FILE, 'r+')
	old_ipv6 = ipv6_filehandler.read().strip()
	ipv6_filehandler.close()
	return old_ipv6 != new_ipv6.strNormal()

def save(new_ipv4, new_ipv6):
	if new_ipv4:
		ipv4_filehandler = open(IPV4_FILE, 'r+')
		ipv4_filehandler.write(new_ipv4.strNormal())
		ipv4_filehandler.close()
	if new_ipv6:
		ipv6_filehandler = open(IPV6_FILE, 'r+')
		ipv6_filehandler.write(new_ipv6.strNormal())
		ipv6_filehandler.close()

