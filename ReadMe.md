### Intro:
`aredn_info.py` does two things:
   1. It reads all `http://[node]/cgi-bin/sysinfo.json?link_info=1&hosts=1&nodes=1`
      pages available on a given network and
   2. It creates `txt` and `csv` output files that synthesize the network
      information for different purposes.

### Usage:
   * Copy all files to a local folder.
   * Edit the optional `exclude_nodes.txt` and `include_nodes.txt` text
     files.
   * Run `python aredn_info.py`
   * The five output files will be saved in the `Output` folder alongside
     `aredn_info.py`

### Some Limitations:
   * API v2.0 has its information in the `nodes` field and doesn't see
     OSLR-only nodes.
   * API v1.14 has its information in the `hosts` field and doesn't see
     Babel-only nodes.
   * Nodes with API v1.13 or older are "invisible" to API v1.14 because
     they don't have the `lan.` prefix, but can be added manually using
     the `include_nodes.txt` file.
   * Nodes with API versions 1.0 or 1.1 will be missing some information.

See  https://arednmesh.readthedocs.io/en/latest/arednHow-toGuides/devtools.html
for more details about the API.
