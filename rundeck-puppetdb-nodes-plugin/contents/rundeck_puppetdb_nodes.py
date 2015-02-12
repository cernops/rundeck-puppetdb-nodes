# Daniel Fernandez Rodriguez <danielfr@cern.ch>

from argparse import ArgumentParser
from requests_kerberos import HTTPKerberosAuth

import json
import requests
import subprocess
import logging

def negociateKRBticket(keytab, username):
    kinit = '/usr/bin/kinit'
    kinit_args = [kinit, '-kt', keytab, username]
    kinit = subprocess.Popen(kinit_args)
    kinit.wait()

def destroyKRBticket():
    subprocess.call(["kdestroy"])

def getFactPuppetDB(apiurl, factname, hostgroup):
    url ='%s/facts/%s' % (apiurl, factname)
    query = '["in", "certname", ["extract", "certname", ["select-facts", ["and", ["=", "name", "hostgroup"], ["~", "value", "%s"]]]]]' % hostgroup
    headers = {'Content-Type': 'application/json','Accept': 'application/json, version=2'}
    payload = {'query': query}
    logging.info("Getting '%s' from '%s', query: '%s'" % (factname, url, query))
    r = requests.get(url, params=payload, headers=headers, verify=False, auth=HTTPKerberosAuth())
    if r.status_code == requests.codes.ok:
        logging.info("Request code: '%s'" % r.status_code)
        return json.loads(r.text)
    logging.error("The request failed with code '%s'" % r.status_code)
    return None

def printNodesList(apiurl, hostgroup):
    '''
    Prints the nodes information in a supported format for Rundeck.
    '''
    operatingsystemfacts = getFactPuppetDB(apiurl, "operatingsystem", hostgroup)
    hostgroupfacts = getFactPuppetDB(apiurl, "hostgroup", hostgroup)
    if not (operatingsystemfacts == None or hostgroupfacts == None):
        logging.info("Printing node list using standard output...")
        for operatingsystem in operatingsystemfacts:
            print (operatingsystem['certname'] + ':')
            print (" "*4+"hostname: "+ operatingsystem['certname'])
            print (" "*4+"username: root")
            for hostgroup in hostgroupfacts:
                if (operatingsystem['certname'] == hostgroup['certname']):
                    print (" "*4+"tags:  hostgroup="+ hostgroup['value'])
            print (" "*4+"osName: "+ operatingsystem['value'])
        logging.info("Node list printed successfully")
    else:
        logging.error("Fact list empty. Check PuppetDB connection params")

def storeNodesList(apiurl, hostgroup, path):
    '''
    Saves the node list in a local file so rundeck can access it localy.
    '''
    operatingsystemfacts = getFactPuppetDB(apiurl, "operatingsystem", hostgroup)
    hostgroupfacts = getFactPuppetDB(apiurl, "hostgroup", hostgroup)
    logging.info("Saving node list in '%s'..." % path)
    if not (operatingsystemfacts == None or hostgroupfacts == None):
        with open("%s/nodes.yaml" % path, 'w') as file:
            for operatingsystem in operatingsystemfacts:
                global counter
                counter = counter + 1
                file.write (operatingsystem['certname'] + ':\n')
                file.write (" "*4+"hostname: "+ operatingsystem['certname']+"\n")
                file.write (" "*4+"username: root\n")
                file.write(" "*4+"tags: ")
                for hostgroup in hostgroupfacts:
                    if (operatingsystem['certname'] == hostgroup['certname']):
		                file.write (" hostgroup="+ hostgroup['value']+"\n")
                file.write (" "*4+"osName: "+ operatingsystem['value']+"\n")
        logging.info("Node list saved successfully")
    else:
        logging.error("Fact list empty. Check PuppetDB connection params")

def puppetdb_nodes_main(apiurl, hostgroup, keytab, username):
    negociateKRBticket(keytab, username)
    #storeNodesList(apiurl, hostgroup, path)
    printNodesList(apiurl, hostgroup)
    destroyKRBticket()

def main():
    parser = ArgumentParser(description="Get rundeck nodes from PuppetDB")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--debug", help="increase output to debug messages", action="store_true")
    parser.add_argument("--apiurl", help="PuppetDB API url (https://<SERVER>:<PORT>/<API VERSION>)", required=True)
    parser.add_argument("--hostgroup", help="Foreman hostgroup", required=True)
    parser.add_argument("--keytab", help="Keytab", required=True)
    parser.add_argument("--username", help="Username to connect to PuppetDB", required=True)
    parser.add_argument("--path", help="Path where the node list will be stored", nargs='?')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)

    puppetdb_nodes_main(args.apiurl, args.hostgroup, args.keytab, args.username)

if __name__ == "__main__":
    main()
