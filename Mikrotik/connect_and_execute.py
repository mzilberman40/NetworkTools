import paramiko
import logging
import argparse
import os
import sys
from typing import List, Dict, Any

# Import the shared function
from parse_hosts import parse_hosts_file

# --- Basic Configuration ---
LOG_FILENAME = '../logs/mikro_manager.log'

# --- Logging Setup ---
# (Logging setup remains specific to this script)
logging.basicConfig(
    filename=LOG_FILENAME,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logging.getLogger().addHandler(console_handler)


def execute_commands_on_host(host_details: Dict[str, Any], commands: List[str]) -> None:
    # This function remains unchanged
    host = host_details.get('host')
    ip = host_details.get('ip')
    port = int(host_details.get('port', 22))
    user = host_details.get('user', 'root')
    key_path = host_details.get('key')
    password = host_details.get('password')

    auth_method = "password" if password else "key" if key_path else "none"
    print(f"\n🔗 Connecting to {host} ({ip}:{port}) using {auth_method} auth...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        connect_params = {"hostname": ip, "port": port, "username": user, "timeout": 10}

        if auth_method == "key":
            if not os.path.exists(key_path):
                logging.error(f"Private key file not found for {host}: {key_path}")
                return
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            connect_params["pkey"] = pkey
            connect_params["disabled_algorithms"] = {'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']}
        elif auth_method == "password":
            connect_params["password"] = password
        else:
            logging.error(f"No valid authentication method (key or password) provided for {host}.")
            return

        client.connect(**connect_params)
        logging.info(f"Successfully connected to {host}.")

        for command in commands:
            print(f"  ▶️  Executing: '{command}'")
            stdin, stdout, stderr = client.exec_command(command)

            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            if output:
                print(f"  ✅ Response:\n{output}\n")
                logging.info(f"SUCCESS for {host} on command '{command}': {output}")
            if error:
                print(f"  ⚠️  Error:\n{error}\n")
                logging.warning(f"STDERR for {host} on command '{command}': {error}")
            if not output and not error:
                print("  ✅ Command executed with no output.\n")
                logging.info(f"SUCCESS for {host} on command '{command}' (no output).")

    except paramiko.ssh_exception.AuthenticationException:
        logging.error(f"Authentication failed for {host}. Please check credentials.")
    except Exception as e:
        logging.error(f"An error occurred with {host}: {e}")
    finally:
        client.close()
        print(f"Connection to {host} closed.")


def main():
    # This function remains unchanged
    parser = argparse.ArgumentParser(
        description="Connect to MikroTik routers via SSH and execute commands.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "hosts_file",
        help="Path to the hosts file."
    )

    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument(
        "-c", "--command",
        nargs='+',
        help="The command(s) to execute on the routers."
    )
    command_group.add_argument(
        "-f", "--file",
        dest="commands_file",
        help="Path to a file containing a list of commands to execute."
    )

    args = parser.parse_args()

    if args.commands_file:
        # We need a small local function here for parsing commands, as it's not shared
        with open(args.commands_file, 'r') as f:
            commands_to_run = [
                line.strip() for line in f
                if line.strip() and not line.strip().startswith(('#', ';'))
            ]
    else:
        commands_to_run = args.command

    if not commands_to_run:
        logging.critical("No commands to execute.")
        return

    hosts = parse_hosts_file(args.hosts_file)
    if not hosts:
        logging.critical("No valid hosts found in the file. Exiting.")
        return

    for host_details in hosts:
        execute_commands_on_host(host_details, commands_to_run)


if __name__ == "__main__":
    main()