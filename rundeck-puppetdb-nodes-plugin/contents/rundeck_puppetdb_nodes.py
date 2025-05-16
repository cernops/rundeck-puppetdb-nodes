from argparse import ArgumentParser
from collections import defaultdict
from requests_kerberos import HTTPKerberosAuth

import json
import requests
import subprocess
import logging
import sys


class PuppetDBNodes():

    def __init__(self, args):
        for k, v in args.items():
            setattr(self, k, v)


    def negociate_krb_ticket(self, keytab_path, krb_principal):
        kinit = '/usr/bin/kinit'
        kinit_args = [kinit, '-kt', keytab_path, krb_principal]
        kinit = subprocess.Popen(kinit_args)
        kinit.wait()


    def destroy_krb_ticket(self):
        subprocess.call(['kdestroy'])


    def get_facts_puppetdb(self, apiurl, facts, hostgroup):

        query_facts = ','.join(['facts.%s' % fact for fact in facts])

        # Strip / to cover cases of where hostgroup has been set to "top/"
        hostgroup_parts = hostgroup.rstrip('/').split('/')
        hostgroup_filter = ' and '.join([f'facts.hostgroup_{i} = "{part}"' for i, part in enumerate(hostgroup_parts)])

        query = 'inventory[certname,%s]{%s}' % (query_facts, hostgroup_filter)

        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, version=2',
                'User-Agent': 'rundeck_puppetdb_nodes/3.1.0'
                }
        payload = {'query': query}

        logging.info("Getting facts from '%s', query: '%s'", apiurl, query)
        r = requests.get(apiurl, params=payload, headers=headers, auth=HTTPKerberosAuth())

        # pylint: disable=no-member
        if r.status_code == requests.codes.ok:
            logging.info("Request code: '%s'", r.status_code)
            return json.loads(r.text)

        logging.error("The request failed with code '%s'", r.status_code)
        return None


    def print_puppetdb_nodes(self, apiurl, hostgroup, sshuser, factlist):
        '''
        Queries PuppetDB and prints out the nodes information in a supported format for Rundeck
.
        '''
        factlist.extend(["os.name", "os.release.full", "hostgroup"])
        raw_data = self.get_facts_puppetdb(apiurl, factlist, hostgroup)
        data = defaultdict(lambda: {})

        if raw_data != None:
            logging.info("Printing node list using standard output...")
            for entry in raw_data:
                print('%s:' % entry['certname'])
                print(" "*4 + "hostname: " + entry['certname'])
                print(" "*4 + "username: " + sshuser)
                for fact in factlist:
                    factkey = "facts.%s" % fact
                    if factkey in entry:
                        print(" "*4 + fact + ": " + str(entry[factkey]))
                        print(" "*4 + factkey + ": " + str(entry[factkey]))
                # legacy facts
                print(" "*4 + "facts.operatingsystem" + ": " + str(entry["facts.os.name"]))
                print(" "*4 + "operatingsystem" + ": " + str(entry["facts.os.name"]))
                print(" "*4 + "facts.operatingsystemrelease" + ": " + str(entry["facts.os.release.full"]))
                print(" "*4 + "operatingsystemrelease" + ": " + str(entry["facts.os.release.full"]))

            logging.info("Node list printed successfully")

        else:
            logging.error('Fact list empty. Check PuppetDB connection params')


    def store_puppetdb_nodes(self, apiurl, hostgroup, sshuser, factlist, filename):
        '''
        Instead of querying PuppetDB every time, saves the list of nodes on a local file
        so Rundeck can access it localy.

        '''
        factlist.extend(["os.name", "os.release.full", "hostgroup"])
        raw_data = self.get_facts_puppetdb(apiurl, factlist, hostgroup)

        if raw_data != None:
            logging.info("Saving node list in '%s'...", filename)
            with open(filename, 'w') as file:
                for entry in raw_data:
                    file.write('%s:' % entry['certname'] + '\n')
                    file.write(" "*4 + "hostname: " + entry['certname'] + '\n')
                    file.write(" "*4 + "username: " + sshuser + '\n')
                    for fact in factlist:
                        factkey = "facts.%s" % fact
                        if factkey in entry:
                            file.write(" "*4 + fact + ": " + str(entry[factkey]) + '\n')
                            file.write(" "*4 + factkey + ": " + str(entry[factkey]) + '\n')
                # legacy facts
                file.write(" "*4 + "facts.operatingsystem" + ": " + str(entry["facts.os.name"]))
                file.write(" "*4 + "operatingsystem" + ": " + str(entry["facts.os.name"]))
                file.write(" "*4 + "facts.operatingsystemrelease" + ": " + str(entry["facts.os.release.full"]))
                file.write(" "*4 + "operatingsystemrelease" + ": " + str(entry["facts.os.release.full"]))

            logging.info('Node list saved successfully')

            # trick to avoid Rundeck complain when no output is printed out
            print("")
        else:
            logging.error('Fact list empty. Check PuppetDB connection params')


    def run(self):
        self.negociate_krb_ticket(self.keytab, self.krbuser)
        if self.store:
            self.store_puppetdb_nodes(self.apiurl, self.hostgroup, self.sshuser, self.factlist, self.file)
        else:
            self.print_puppetdb_nodes(self.apiurl, self.hostgroup, self.sshuser, self.factlist)


def main():
    parser = ArgumentParser(description="Populate Rundeck list of nodes from PuppetDB")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--debug", help="increase output to debug messages", action="store_true")

    parser.add_argument("--apiurl", help="PuppetDB API url (https://<SERVER>:<PORT>/<API VERSION>)", required=True)
    parser.add_argument("--hostgroup", help="Foreman hostgroup", required=True)
    parser.add_argument("--keytab", help="Absolute path to kerberos principals keytab (used to authenticate & connect to PuppetDB)", required=True)
    parser.add_argument("--krbuser", help="Kerberos principal (used alongside 'keytab' to connect to PuppetDB)", required=True)
    parser.add_argument("--sshuser", default="root", help="User Rundeck will use to connect to hosts via SSH", required=True)
    parser.add_argument("--factlist", nargs="*", default=[], help="List of facts to retrieve for every node")
    parser.add_argument("--file", default="/tmp/nodes.yaml", help="File path where the node list info will be stored")

    behaviour = parser.add_mutually_exclusive_group()
    behaviour.add_argument("--store", action="store_true")
    behaviour.add_argument("--print", action="store_false")

    args = parser.parse_args()

    #trick to get the factlist as an object list when called it from Rundeck
    if len(args.factlist) == 1:
        args.factlist = args.factlist[0].split()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)

    plugin = PuppetDBNodes(args.__dict__)
    plugin.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
        sys.exit(-1)
