# DDNS-NG

Notice: This project is not actively maintained anymore. Use at your own risk.

## Introduction
A modular Dynamic DNS updater supporting IPv4 (A) and IPv6 (AAAA) records.
Through modules, you can choose between different methods to determine and
update your DNS records:

## Modules
### Pre-checkers:
Optional. Determine, if anything needs to be done at all, before contacting external servers.
E.g. this could be a module that attempts to access a resource on your own server via public DNS.
If the attempt is successful, the DNS records are still up to date and nothing needs to be done.
#### The following modules are available:
* dummy: The pre-check always fails and the process always continues

### IP retrievers:
These modules determine your external IPv4 and IPv6 addresses.
You can choose a list of modules. The first IPv4 and IPv6 addresses returned will be used.
#### The following modules are available:
* fritzbox_v4: Determines your public IPv4 address from your Fritzbox router. Requires configuration of the IP address of your Fritzbox in the module source code.
* upnp_v4: Determines your public IPv4 address from your UPnP-enabled home router (should work with Fritzboxes, too)
* web_v4: Uses an external web service to determine your public IPv4 address
* linux_v6: Determines your public IPv6 address locally on Linux machines by running the "ip" command. Requires configuration of your network interface in the module source code.

### Old IP checkers:
Optional. These modules check if the IP addresses determined in the previous step are different from those in your DNS.
Only if an IP address changed compared to the last run, the script continues to update the DNS.
#### The following modules are available:
* dummy: Always reports the IP addresses as having changed, so that the DNS update is always run.
* localfile: Compares the currently determined IP addresses to those of the previous run, which are stored in plain text files.

### DNS updaters:
These modules update your DNS records with the new IP addresses.
#### The following modules are available:
* cloudflare: Update your DNS records via Cloudflare's API. Requires configuration in the module's cloudflare.ini file.

## Installation
DDNS-NG requires Python 3. The only nonstandard Python module it depends on is "ipy" (https://github.com/autocracy/python-ipy/), and when using the `upnp_v4` IP retriever, "miniupnpc".

Clone or download the git repository onto your server, choose your modules in the config.ini file and configure any modules, if required.

To run the script every five minutes, you could add the following line to your cron jobs (run `crontab -e`):

`*/5 * * * * /opt/ddns-ng/ddns-ng.py >> /opt/ddns-ng/log.txt 2>&1`