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

# Basic module to retrieve the public IPv4 address from the router via UPnP

def getIP():
	import miniupnpc
	u = miniupnpc.UPnP()
	u.discoverdelay = 200
	ndevices = u.discover()
	if ndevices == 0:
		print("ERROR: Could not find UPnp devices.")
		return None
	u.selectigd()
	return u.externalipaddress()
	
