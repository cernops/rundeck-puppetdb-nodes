Rundeck PuppetDB Nodes Plugin
=============================================

Description
-----------
This is a Resource Model Source plugin for [Rundeck][] Rundeck version 2.0 (or higher) that retrieves node definitions
from PuppetDB.

Developed in Python, it uses [python-requests][] library and Kerberos authentication to connect to the PuppetDB API.

[RunDeck]: http://rundeck.org
[python-requests]: http://docs.python-requests.org/en/latest/

Either the puppetdb API url, the foreman hostgroup, username, and the kerberos keytab path can be specified via plugin parameters on the project's configuration page.

Parameters
----------
`PuppetDB` - PuppetDB API URL following this format: `https://<SERVER>:<PORT>/<API VERSION>`

 > `https://my.puppet.db:2525/v3`

`Foreman Hostgroup` - Specify a Foreman hosgroup to filter the query

 > `cloud_workflow` or `cloud_`

`Factlist` - Space-separated list of facts to retrieve for every node

`Kerberos user` - Kerberos principal (used alongside 'keytab' to connect to PuppetDB)

`Kerberos keytab` - Absolute path to kerberos principal's keytab (used to authenticate & connect to PuppetDB)

`SSH User` - User Rundeck will use to connect to hosts via SSH

`Execution Mode` - Prints out/stores on file the list of nodes. Select store if you want to cache the result

`Output file` - Save list of nodes to file (only if 'store' mode selected)


Requirements
------------
* The plugin requires Rundeck version 2.0 or higher.
* Python 3.
* python-requests v1.1.0-4 or higher
* python-requests-kerberos v0.5 ([important!!](https://bugzilla.redhat.com/show_bug.cgi?id=1169296)) or higher

Installation
------------
Download the latest .ZIP from the [releases page](https://github.com/cernops/rundeck-puppetdb-nodes/releases) and copy it to `/var/lib/rundeck/libext/`. Restart the Rundeck service to be sure it gets the lastest changes.

Next time you log in, you will see a new Resource Model Source called **PuppetDB Source** on the project's configuration page.

Running Plugin Manually
-----------------------

```bash
python3 rundeck_puppetdb_nodes.py --verbose --apiurl https://pdb.example.ch:9081/pdb/query/v4 \
    --hostgroup one/two\
    --krbuser $USER --sshuser $USER \
    --keytab /tmp/foo \
    --store --file /tmp/foo.yaml
```

or

```bash
python3 rundeck_puppetdb_nodes.py --verbose --apiurl https://pdb.example.ch:9081/pdb/query/v4 \
    --hostgroup one/two\
    --krbuser $USER --sshuser $USER \
    --keytab /tmp/foo \
```

Plugin Output example
---------------------

```yaml
nodeA.example.ch:
    hostname: nodeA.example.ch
    username: fred
    os.name: RedHat
    facts.os.name: RedHat
    os.release.full: 9.5
    facts.os.release.full: 9.5
    hostgroup: one/two/login
    facts.hostgroup: one/two/login
    facts.operatingsystem: RedHat
    operatingsystem: RedHat
    facts.operatingsystemrelease: 9.5
    operatingsystemrelease: 9.5
nodeB.example.ch:
    hostname: nodeB.example.ch
    username: straylen
    os.name: RedHat
    facts.os.name: RedHat
    os.release.full: 9.5
    facts.os.release.full: 9.5
    hostgroup: one/two/login
    facts.hostgroup: one/two/login
    facts.operatingsystem: RedHat
    operatingsystem: RedHat
    facts.operatingsystemrelease: 9.5
    operatingsystemrelease: 9.5
```
