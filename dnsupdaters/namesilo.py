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

# Basic module to update DNS records on CloudFlare

import os
import sys
import configparser
import requests
import xml.etree.ElementTree as ET

import pprint
pp = pprint.PrettyPrinter(indent=4)

# Namesilo API version
NS_Version = "1"

# Determine config file path
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "namesilo.ini")

# Check if the config file exists
if not os.path.isfile(config_file):
	sys.exit("Could not find the configuration file for the namesilo module. Please check that the dnsupdaters/namesilo.ini file is readable.")

# Read config file
config = configparser.ConfigParser()
config.read(config_file) # TODO: throw exception if invalid config file?

def update(new_ipv4, new_ipv6):
	# Create a list of record IDs we want to update
	for domain in config.sections():
		# obtain zone ID
		request_params = {
			'version': NS_Version,
			'type': "xml",
			'key': config.get('DEFAULT', 'NS_Key'),
			'name': domain
		}
		r = requests.get('https://www.namesilo.com/api/dnsListRecords', params=request_params)
		if r.status_code != 200:
			sys.exit(f"Unexpected status code while loading records for '{domain}': {r.status_code}")
		response = ET.fromstring(r.text)
		if response.find("reply").find("code").text != "300":
			sys.exit(f"Retrieving DNS records for '{domain}' failed. Response code: {response.find('reply').find('code').text}")
		
		# Create list of subdomains for this domain from config option
		subdomains = config.get(domain, 'NS_Subdomains').split(',')
		
		# Walk through all the records in the zone, check for those which match our list of subdomains and then update
		for xmlrecord in response.find("reply").findall("resource_record"):
			record = {}
			record["id"] = xmlrecord.find("record_id").text
			record["type"] = xmlrecord.find("type").text
			record["host"] = xmlrecord.find("host").text
			record["value"] = xmlrecord.find("value").text
			
			# Check if record is in out list of subdomains and then update
			if (((new_ipv4 and record['type'] == 'A') or (new_ipv6 and record['type'] == 'AAAA')) and \
					(record['host'] in subdomains or record['host'].rsplit('.' + domain, 1)[0] in subdomains)
					):
					# If this record already has the correct IP, we return early
					# and don't do anything.
					if ((record['type'] == 'A' and record['value'] == new_ipv4.strNormal()) or (record['type'] == 'AAAA' and record['value'] == new_ipv6.strNormal())):
						if not config.getboolean('DEFAULT', 'quiet'):
							print(f"Record '{record['host']}' does not require updating.")
					else:
						# Update the record with the new IP address
						if record['type'] == 'A':
							new_ip = new_ipv4.strNormal()
							new_ttl = int(config.get('DEFAULT', 'NS_TTL_A'))
						else:
							new_ip = new_ipv6.strNormal()
							new_ttl = int(config.get('DEFAULT', 'NS_TTL_AAAA'))
						
						request_params = {
							'version': NS_Version,
							'type': "xml",
							'key': config.get('DEFAULT', 'NS_Key'),
							'domain': domain,
							'rrid': record['id'],
							'rrhost': record['host'],
							'rrvalue': new_ip,
							'rrttl': new_ttl
						}
						r = requests.get('https://www.namesilo.com/api/dnsUpdateRecord', params=request_params)
						if r.status_code != 200:
							sys.exit(f"Unexpected status code while updating '{record['host']}': {r.status_code}")
						response = ET.fromstring(r.text)
						if response.find("reply").find("code").text == "300":
							if not config.getboolean('DEFAULT', 'quiet'):
								print(f"Updated '{record['host']}' with '{new_ip}'")
						else:
							sys.exit(f"Updating '{record['host']}' with '{new_ip}' failed. Response code: {response.find('reply').find('code').text}")
