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

Plugin Output example
---------------------
```
scheduler-02.mydomain.com:
    hostname: scheduler-02.mydomain.com
    username: root
    tags:  hostgroup=workflows/scheduler/server
    osName: SLC
scheduler-01.mydomain.com:
    hostname: scheduler-01.mydomain.com
    username: root
    tags:  hostgroup=workflows/scheduler/server
    osName: SLC
loadbalancer-01.mydomain.com:
    hostname: loadbalancer-01.mydomain.com
    username: root
    tags:  hostgroup=workflows/ha
    osName: SLC
server-02.mydomain.com:
    hostname: server-02.mydomain.com
    username: root
    tags:  hostgroup=workflows/server/production
    osName: SLC
loadbalancer-02.mydomain.com:
    hostname: loadbalancer-02.mydomain.com
    username: root
    tags:  hostgroup=workflows/ha
    osName: SLC
server-qa-01.mydomain.com:
    hostname: server-qa-01.mydomain.com
    username: root
    tags:  hostgroup=workflows/server/qa
    osName: SLC
loadbalancer-qa-01.mydomain.com:
    hostname: loadbalancer-qa-01.mydomain.com
    username: root
    tags:  hostgroup=workflows/ha
    osName: SLC
server-qa-03.mydomain.com:
    hostname: server-qa-03.mydomain.com
    username: root
    tags:  hostgroup=workflows/server
    osName: CentOS
server-datastore.mydomain.com:
    hostname: server-datastore.mydomain.com
    username: root
    tags:  hostgroup=workflows/datastore
    osName: CentOS
server-qa-02.mydomain.com:
    hostname: server-qa-02.mydomain.com
    username: root
    tags:  hostgroup=workflows/server
    osName: SLC
```
