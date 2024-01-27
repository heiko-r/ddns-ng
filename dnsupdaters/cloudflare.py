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
import json

import pprint
pp = pprint.PrettyPrinter(indent=4)

# Determine config file path
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cloudflare.ini")

# Check if the config file exists
if not os.path.isfile(config_file):
	sys.exit("Could not find the configuration file for the cloudflare module. Please check that the dnsupdaters/cloudflare.ini file is readable.")

# Read config file
config = configparser.ConfigParser()
config.read(config_file) # TODO: throw exception if invalid config file?

def update(new_ipv4, new_ipv6):
	# General request headers (authentication)
	request_headers = {
		'X-Auth-Email':	config.get('DEFAULT', 'CF_Email'),
		'X-Auth-Key':	config.get('DEFAULT', 'CF_Key'),
		'Content-Type':	'application/json',
		'User-Agent':	'ddns-ng/0.1alpha'
	}
	
	# Create a list of record IDs we want to update
	for domain in config.sections():
		# obtain zone ID
		request_params = {
			'name':	domain
		}
		r = requests.get('https://api.cloudflare.com/client/v4/zones', params=request_params, headers=request_headers)
		if r.status_code != 200:
			sys.exit(f'Unexpected status code while loading zone: {r.status_code}')
		response = json.loads(r.text)
		zone_id = response['result'][0]['id']
		
		# Create list of subdomains for this domain from config option
		subdomains = config.get(domain, 'CF_Subdomains').split(',')
		
		# Walk through all the records in the zone, check for those which match our list of subdomains and then update
		# Results may be paginated, so loop over each page.
		has_more = True
		page = 1
		while has_more:
			# Retrieve list of DNS records
			request_params = {
				'page':			page,
				'per_page':		10,
				'order':		'name',
				'direction':	'asc'
			}
			r = requests.get('https://api.cloudflare.com/client/v4/zones/' + zone_id + '/dns_records', params=request_params, headers=request_headers)
			if r.status_code != 200:
				sys.exit(f'Unexpected status code while loading DNS records for { domain }: {r.status_code}')
			response = json.loads(r.text)
			
			# Check if record is in out list of subdomains and then update
			for record in response['result']:
				if (((new_ipv4 and record['type'] == 'A') or (new_ipv6 and record['type'] == 'AAAA')) and \
					(record['name'] in subdomains or record['name'].rsplit('.' + domain, 1)[0] in subdomains)
					):
					# If this record already has the correct IP, we return early
					# and don't do anything.
					if ((record['type'] == 'A' and record['content'] == new_ipv4.strNormal()) or (record['type'] == 'AAAA' and record['content'] == new_ipv6.strNormal())):
						if not config.getboolean('DEFAULT', 'quiet'):
							print(f"Record '{record['name']}' does not require updating.")
					else:
						record_id = record['id']
						
						# Update the record with the new IP address
						
						if record['type'] == 'A':
							new_ip = new_ipv4.strNormal()
							new_ttl = int(config.get('DEFAULT', 'CF_TTL_A'))
						else:
							new_ip = new_ipv6.strNormal()
							new_ttl = int(config.get('DEFAULT', 'CF_TTL_AAAA'))
						
						request_data = json.dumps({
							'content':	new_ip,
							'type':		record['type'],
							'name':		record['name'],
							'ttl':		new_ttl,
							'proxied':	config.getboolean('DEFAULT', 'CF_Proxy')
						})
						r = requests.put(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}', data=request_data, headers=request_headers)
						if r.status_code != 200:
							print("text: " + r.text)
							pp.pprint(r.headers)
							sys.exit(f"Unexpected status code while updating DNS records for {record['name']}: {r.status_code}")
						upd_response = json.loads(r.text)
						if upd_response['success'] is True:
							if not config.getboolean('DEFAULT', 'quiet'):
								print(f"Updated '{record['name']}' with '{new_ip}'")
						else:
							sys.exit(f"Updating '{record['name']}' with '{new_ip}' failed: {upd_response['errors']}")
			# Check if the response was paginated and if so, call another page
			if response['result_info']['total_pages'] > page:
				# Set a new start point
				page += 1
			else:
				has_more = False

