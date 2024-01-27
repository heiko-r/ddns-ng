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

# Basic submodule to retrieve the public IPv4 address by querying a fritzbox via upnp

from subprocess import CalledProcessError


FRITZBOX_IP = "192.168.1.1"
FRITZBOX_PORT = 49000

def getIP():
	from subprocess import check_output
	try:
		return check_output(f'upnpc -u http://{FRITZBOX_IP}:{FRITZBOX_PORT}/igddesc.xml -s | grep ^ExternalIPAddress | cut -c 21-', shell=True).strip()
	except CalledProcessError as err:
		print(f'ERROR: Failed to retrieve IPv4 address: {err}')
		return None
		
	
