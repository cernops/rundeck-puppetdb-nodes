# Changelog

All notable changes to this project will be documented in this file.

## Unreleased
- Expose both "fact" and "facts.fact" as keys.
- Use non legacy facts in query
- Maintain old legacy facts "operatingsystem" and "operatingsystemrelease"
  derived from their non-legacy fact versions.

## [v3.0.0](https://github.com/cernops/rundeck-puppetdb-nodes/tree/v3.0.0)
- Use PDB /inventory endpoint
- Explode full hostgroup and query with hostgroup elements

## [v2.1.0](https://github.com/cernops/rundeck-puppetdb-nodes/tree/v2.1.0)

- Set custom user-agent for puppetdb requests to "rundeck_puppetdb_nodes"
