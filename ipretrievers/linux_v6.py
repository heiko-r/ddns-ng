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

# Basic module to retrieve the public, global IPv6 address locally

from subprocess import CalledProcessError


DEVICE = "eth0"

def getIP():
	from subprocess import check_output
	try:
		return next(filter(lambda x: x.startswith('2'), check_output(r"ip -6 addr show dev eth0 scope global | sed -e's/^.*inet6 \([^ ]*\)\/.*$/\1/;t;d'", shell=True, universal_newlines=True).strip().split("\n")))
	except CalledProcessError as err:
		print(f"ERROR: Failed to retrieve IPv6 address: {err}")
		return None
