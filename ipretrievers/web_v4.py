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

# Basic module to retrieve the public IPv4 address from a web service

IPV4_URL = "http://v4.ipv6-test.com/api/myip.php"

def getIP():
	import requests
	r = requests.get(IPV4_URL)
	if  r.status_code >= 200 and r.status_code < 300:
		return r.text
	else:
		print(f"Error when fetching IPv4 URL: Status code: {r.status_code}")
		return None
