Intro:
aredn_info.py does two things:
    1. It reads all   sysinfo.json?link_info=1&hosts=1&nodes=1   pages available
       on a given network and
    2. creates output files that synthesize the information.

How to use:
    * Copy all five files to a folder.
    * Edit the  exclude_nodes.txt  and  include_nodes.txt  text files.
    * Run aredn_info.py
    * The four output files will be saved in the same folder as  aredn_info.py

Some limitations:
    * API v2.0 has its information in the nodes field and doesn't see OSLR-only nodes.
    * API v1.14 has its information in the hosts field and doesn't see Babel-only nodes.
    * Nodes with API v1.13 or older are "invisible" to API v1.14 but can
      be added manually using the    include_nodes.txt    file.
    * Nodes with API versions 1.0 or 1.1 will be missing some information.

See   https://arednmesh.readthedocs.io/en/latest/arednHow-toGuides/devtools.html
for more details about the API.


CHANGE LOG:

    * v2025.12.11
        - made using a babel-only node optional by entering "N" at the prompt.
        - added the option to read "include_nodes.txt" to manually include nodes
          with API v1.13 and older since they don't have the "lan." prefix and
          are ignored.
        - added the option to read "exclude_nodes.txt" to manually exclude nodes.
        - cleaned up the code a bit.

    * v2025.11.30
        - nodes from API v1.14 are now filtered using "lan." in [0:4]
        - nodes from API v2.0 are extracted from the "nodes" field instead of
          "hosts"
        - as a result, there is no need to manually maintain  lan_hostnames.txt
        - lowered the timeout from 60 seconds to 15 seconds.
        - fixed the number of concurent downloads to 30.

    * V2025.11.02
        - API v1.14 does NOT show Babel-only nodes so I added a second API query
          to a Babel-only node (with API v2.0) which shows Babel-only nodes
          but not OSLR-only nodes.  I then add the difference to the nodes array.
          (lines 133 - 145, 170 - 173)

    * V2025.06.23
        - Changed default number of concurent downloads from 100 to 30 (line 47)

    * V2025.04.19
        - Added casefold() to hosts[host] (line 151)

    * v2025.04.07
        - Ignore hostnames that start with 'lan.' (line 156)

    * v2023.12.10
        - Ignore case in   lan_hostname

    * v2023.11.28
        - Updated syntax to modern formatted string literals.

    * v2023.11.21
        - Added an alternative script_path for use on Windows.
 
    * v2023.11.14
        - Fixed a minor bug to ensure that num_of_threads is an integer.

    * v2023.11.13
        - Fixed minor bug where some of the connections in the Diagrams_Net.txt
          file were duplicated resulting in nodes with two lines in the diagram.
          The issue was that I had the api_v as the forth element of topo and
          topo_inv, which meant that the condition if   tuple in topo_inv[0:i]
          wasn't catching duplicates if they had different API versions.
        - Added   input()   functions a the beginning so user can enter a
          different starting node than   va7fi-hapac3-1   and a number of
          concurrent downloads.
        - Added a line at the top of  Diagrams_Net.txt  and  Topology_List.txt
          with the number of nodes and connections found.

    * v2023.11.12
        - Re-wrote the whole thing from scratch to use the json files from the
          API instead of scraping the html
        - Renamed it aredn_info.py and consolidated all the code under one file.
        - Still a few things to cleanup and add, but it's functional and much
          faster than the previous versions.
        - Note that some information might be missing if the API version <= 1.1

    * v2023.10.28b
        - Removed urls[] list so that the code is more general.

    * v2023.10.28a
        - Modified read_pages.py so that it can read the new layout of the
          Mesh Status page.
        - Fixed a small bug in read_pages.py where code was expecting
          plural neibhors and nodes instead of neibhor* and node*
          (lines 175 and 179)
        - Also updated my node URL on lines 39 and 40

    * v2021.12.20
        - Broke the code into different files.

    * v2021.12.16:
        - Code cleanup.  No new features.

    * v2021.12.14:
        - Set maximum number of concurrent threads to 30 to optimize the speed.
        - This version can take less than 10 seconds to process 85 stations.
        - Added two csv output pages.

    * v2021.12.13:
        - Code cleanup.  No new features.

    * v2021.12.10:
        - Uses threading to download all status pages into pages[].
        - It increased the speed by a factor of 5 to 10.

    * v2021.12.05:
        - Uses a list nodes2[] to organize information, which can then easily
          be formatted different ways.
        - Added format for diagrams.net and re-wrote flowchart.fun
        - Added Human Readable output list.

    * v2021.11.12:
        - First working draft.
        - Takes about 3 minutes to process 85 stations.
