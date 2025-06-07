import os
import sys
from typing import List, Dict, Any


# This function is now in a central, reusable location.
def parse_hosts_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Parses a hosts file for connection details. Skips commented or malformed lines.
    """
    if not os.path.exists(filepath):
        # Use logging if available, otherwise print and exit.
        # This makes the function usable even without a complex logging setup.
        print(f"CRITICAL: Hosts file not found at '{filepath}'. Aborting.")
        sys.exit(1)

    hosts_config = []
    with open(filepath, 'r') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith(('#', ';')):
                continue

            parts = line.split()
            host_details = {}
            for part in parts:
                try:
                    key, value = part.split('=', 1)
                    host_details[key.lower()] = value
                except ValueError:
                    print(f"WARNING: Malformed entry on line {i} in '{filepath}': '{part}'. Skipping part.")
                    continue

            if 'host' not in host_details or 'ip' not in host_details:
                print(f"WARNING: Line {i} in '{filepath}' is missing 'host' or 'ip'. Skipping line.")
                continue

            # Expand tilde and normalize path for cross-platform compatibility
            if 'key' in host_details:
                path = os.path.expanduser(host_details['key'])
                host_details['key'] = os.path.normpath(path)

            hosts_config.append(host_details)

    return hosts_config