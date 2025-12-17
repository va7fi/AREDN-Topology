#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
LICENSE:
Copyright (C) 2025 Patrick Truchon.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import time
import urllib.request as urlr
import threading
import fnmatch
import sys
import json
import os

# Some variables:
global json_pages
date_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
num_of_threads = 30
timeout = 15
olsr_node = 'VE7NA-RADIO-ROOM'
babel_node = 'VE7ZDH-tube-1'

# Get script path and create Output folder if it doesn't exist.
if sys.platform == 'win32':
    script_path = os.path.abspath(__name__).rpartition('\\')[0]+'\\'
    output_path = script_path + 'Output\\'
else:
    script_path = os.path.abspath(__file__).rpartition('/')[0]+'/'
    output_path = script_path + 'Output/'

if not os.path.exists(output_path):
    os.makedirs(output_path)

# Some user input variables:
olsr_message = 'Enter your node id or simply press Enter to use:'
babel_message = 'Enter a BABEL-ONLY node id, press Enter to use:'
print('#' * 75)
print(f'{olsr_message}  {olsr_node}')
my_node1 = input().casefold() or olsr_node
print(f'{babel_message}  {babel_node} , or Enter "N" to skip.')
my_node2 = input().casefold() or babel_node


# Progress Bar:
def progress_bar(progress, total, start_time):
    '''
    Displays and updates a console progress bar.  Modified from:
    https://stackoverflow.com/questions/3160699/python-progress-bar
    '''
    bar_length = 57
    status = ''
    ratio = float(progress) / float(total)
    time_interval = f'{(time.monotonic() - start_time):0.0f}s'
    if ratio >= 1.:
        ratio = 1
        status = '\r\n'
    block = int(round(bar_length * ratio))
    text = f'\r[{"#" * block + "-" * (bar_length - block)}] ' +  \
        f'{progress:.0f}/{total:.0f} {time_interval} {status}'
    sys.stdout.write(text)
    sys.stdout.flush()


# Download two initial json files to build a list of nodes
json_error = '''sysinfo.json from your node could not be loaded.
   *  check that you are connected to AREDN
   *  and that the following URL is valid:
'''

# For API v1.14, use hosts=1
my_url1 = f'http://{my_node1}.local.mesh/cgi-bin/' \
    + 'sysinfo.json?link_info=1&hosts=1'
try:
    my_json1 = json.loads(urlr.urlopen(my_url1, timeout=timeout).read())
except:
    print(f'{json_error}      {my_url1}  \n')
    exit()

# For API v2, use nodes=1
my_url2 = f'http://{my_node2}.local.mesh/cgi-bin/' \
    + 'sysinfo.json?link_info=1&nodes=1'

if my_node2 != 'n':
    try:
        my_json2 = json.loads(urlr.urlopen(my_url2, timeout=timeout).read())
    except:
        print(f'{json_error}      {my_url2}  \n')
        exit()


# Build combined list of visible nodes.
nodes = []

# Read exclude_nodes.txt
ignore_nodes = []
if os.path.exists(script_path + 'exclude_nodes.txt'):
    with open(script_path + 'exclude_nodes.txt') as file:
        for line in file:
            if (line[0] != "#" and not line.isspace()):
                ignore_nodes.append(line.strip())
    file.close()

# Read my_json1 and extract hosts from {'hosts': [{'name' : host}]}.
for host in my_json1.get('hosts', ''):
    if (host['name'][0:4] == 'lan.' and
            host['name'][4:-11].casefold() not in ignore_nodes):
        nodes.append(host['name'][4:-11].casefold())

# Read my_json2 and extract the nodes that were not in my_json1.
if my_node2 != 'n':
    for host in my_json2.get('nodes', ''):
        if (host['name'].casefold() not in nodes and
                host['name'].casefold() not in ignore_nodes):
            nodes.append(host['name'].casefold())

# Read include_nodes.txt
if os.path.exists(script_path + 'include_nodes.txt'):
    with open(script_path + 'include_nodes.txt') as file:
        for line in file:
            if (line[0] != "#" and not line.isspace()):
                nodes.append(line.strip())
    file.close()

nodes = sorted(nodes, key=str.lower)


# For each node, download the json pages and build a dictionary
json_pages = {}     # {node:json_page, ...}
failed_nodes = []   # Nodes that failed to download.


def download_json(node):
    '''
    Download json page for a node. Called repeatedly by the Threading process.
    Some older firmware versions seem to require the 8080 port number.
    '''
    suffix = '.local.mesh:8080/cgi-bin/sysinfo.json?link_info=1'
    url = f'http://{node}{suffix}'

    t_0 = time.monotonic()
    try:
        json_page = json.loads(urlr.urlopen(url, timeout=timeout).read())
        json_pages[node] = json_page        # Build the main dictionary.
        t_1 = time.monotonic()
        delta_time = t_1 - t_0
    except:
        failed_nodes.append(node)           # Note the failed nodes.
        t_1 = time.monotonic()
        delta_time = t_1 - t_0
        pass


# Download multiple json pages at the same time to improve run time.
end = len(nodes)        # Total number of pages to download
start = 0               # First thread.  This will change as it progresses
threads = []

# In case where the number of nodes is less than the optimum number of threads:
if end < num_of_threads:
    stop = end
else:
    stop = num_of_threads

download_message = f'''
Attempting to download {len(nodes):0.0f} json pages.
(Unreachable nodes will timeout after {timeout:0.0f} seconds.)'''
print(download_message)

# This loops starts the multiple downloads, but exits before they are finished.
t_0 = time.monotonic()
alive = True
while alive:
    progress_bar(len(json_pages), len(nodes), t_0)

    # Set up the downloads between start and stop:
    for i in range(start, stop):
        node = nodes[i]
        thread = threading.Thread(target=download_json, args=(node, ))
        threads.append(thread)

    # Start the multi threading:
    for t in threads[start:]:
        t.start()

    # If all pages have finished downloading exit this loop
    alive = False
    for t in threads:
        alive = alive or t.is_alive()

    if not alive:
        break

    # Wait and calculate how many more pages to start downloading next:
    time.sleep(1)
    start = stop
    stop = stop + num_of_threads - threading.active_count()

    # Make sure that stop doesn't go over the total number of pages expected.
    if stop > end:
        stop = end

# Joining any remaining threads before continuing (just in case).
for t in threads:
    t.join()

t_1 = time.monotonic()
delta_time = t_1 - t_0

# Print Download Results
print(f'\n{len(json_pages)} / {len(nodes)} pages were downloaded.')

if len(failed_nodes) > 1:
    print(f'{len(failed_nodes)} pages were not downloaded: '
          + str(failed_nodes)[1:-1].replace("'", ""))

elif len(failed_nodes) > 0:
    print(f'{len(failed_nodes)} page was not downloaded: '
          + str(failed_nodes)[1:-1].replace("'", ""))

# Remove failed_nodes from nodes
for failed_node in failed_nodes:
    nodes.remove(failed_node)


# Write output files:
files = []
topo = []
topo_inv = []

# Create two lists of tuples:
#   * topo = [(node, node2, link_type)]
#   * topo_inv = [(node2, node, link_type]
for node in nodes:
    jp = json_pages[node]
    api_v = float(jp.get('api_version', ''))
    if api_v <= 1.1 or jp.get('link_info', '') == '':
        topo.append((node, '', ''))
        topo_inv.append(('', node, ''))
    else:
        for ip in jp.get('link_info', ''):
            node2 = jp.get('link_info', '').get(ip).get('hostname')
            node2 = node2.partition('.local.mesh')[0]
            node2 = node2.replace('.', '')
            node2 = node2.casefold()
            link_type = jp.get('link_info', '').get(ip).get('linkType')
            if link_type == 'WIREGUARD':
                link_type = 'WRGRD'
            topo.append((node, node2, link_type))
            topo_inv.append((node2, node, link_type))

# Diagrams_Net.txt
files.append('Diagrams_Net.txt')
instructions = ''';
;INSTRUCTIONS:
;Go to https://app.diagrams.net
;Create a New Diagram
;Choose a Blank Diagram
;Click the + sign
;Select Advanced > From Text
;Select Diagram instead of List
;Delete the example and copy and paste the content of this file
;Click on View > Format Panel
;Right-click in the white space and Select Edges
;In the Format Panel, replace the arrow below the 1pt by None
;Move nodes1 around as needed

'''
link_num = 1
lines = []
for i, tuple in enumerate(topo):
    if tuple[1] == '' or tuple in topo_inv[0:i]:
        pass
    else:
        lines.append(f'{tuple[0]}->{tuple[2]}->{tuple[1]}\n')
        link_num = link_num + 1

with open(output_path + date_time + '_Diagrams_Net.txt', 'w') as file:
    file.write(f';Found {len(nodes)} nodes and {link_num} connections.\n')
    file.write(instructions)
    for line in lines:
        file.write(line)
file.close()

# Topology_List.txt
files.append('Topology_List.txt')
with open(output_path + date_time + '_Topology_List.txt', 'w') as file:
    file.write(f'Found {len(nodes)} nodes and {link_num} connections.\n\n')
    for i, tuple in enumerate(topo):
        jp = json_pages[tuple[0]]
        api_v = float(jp.get('api_version', ''))
        if api_v <= 1.1:
            file.write(tuple[0] + '\n')
            file.write('   * The firmware is too old to get list.\n')
        elif tuple[1] == '':
            file.write(tuple[0] + '\n')
        elif i == 0:
            file.write(tuple[0] + '\n')
            file.write(f'   * {tuple[1]} ({tuple[2]})\n')
        elif topo[i-1][0] == topo[i][0]:
            file.write(f'   * {tuple[1]} ({tuple[2]})\n')
        else:
            file.write(tuple[0] + '\n')
            file.write(f'   * {tuple[1]} ({tuple[2]})\n')
file.close()

# Topology.csv
files.append('Topology.csv')
header = 'Node 1,Node 2,Link Type\n'
with open(output_path + date_time + '_Topology.csv', 'w') as file:
    file.write(header)
    for tuple in topo:
        jp = json_pages[tuple[0]]
        api_v = float(jp.get('api_version', ''))
        if api_v <= 1.1:
            file.write(f'{tuple[0]},The firmware is too old to get list')
        else:
            for elem in tuple:
                file.write(str(elem))
                file.write(',')
        file.write('\n')
file.close()

# Node_Info.csv
files.append('Node_Info.csv')
header = 'Node,Lat,Lon,Grid Square,Desc,Firmware,API,Description,Uptime,' \
    + 'Channel,Bandwidth \n'

with open(output_path + date_time + '_Node_Info.csv', 'w') as file:
    file.write(header)
    for node in nodes:
        line = []
        jp = json_pages[node]
        api_v = float(jp.get('api_version'))
        line.append(node)
        line.append(jp.get('lat', ''))
        line.append(jp.get('lon', ''))
        line.append(jp.get('grid_square', ''))

        if api_v > 1.1:
            line.append(jp.get('node_details', '').get('description', ''))
            line.append(jp.get('node_details', '').get('firmware_version', ''))
            line.append(jp.get('api_version'))
            line.append(jp.get('node_details', '').get('model', ''))
            line.append(jp.get('sysinfo', '').get('uptime', ''))
            line.append(jp.get('meshrf', '').get('channel', ''))
            line.append(jp.get('meshrf', '').get('chanbw', ''))
        else:
            line.append(jp.get('description', ''))
            line.append(jp.get('firmware_version', ''))
            line.append(jp.get('api_version'))
            line.append(jp.get('model', ''))
            line.append(jp.get('uptime', ''))
            line.append(jp.get('channel', ''))
            line.append(jp.get('chanbw', ''))

        for elem in line:
            file.write(f'"{elem}",')
        file.write('\n')
file.close()

# Final Message
files.sort()
print()
print(f'These output files were saved in   {output_path}')
for file in files:
    print(f'  * {date_time}_{file}')
print()
print('Press Enter to quit')
input()
