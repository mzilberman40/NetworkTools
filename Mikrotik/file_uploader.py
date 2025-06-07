import paramiko
import logging
import argparse
import os
import sys
from typing import List, Dict, Any

# Import the shared function
from parse_hosts import parse_hosts_file

# --- Basic Configuration ---
LOG_FILENAME = '../logs/file_uploader.log'

# --- Logging Setup ---
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


def upload_file_to_host(host_details: Dict[str, Any], local_path: str, remote_path: str) -> None:
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

        sftp = client.open_sftp()
        print(f"  ▶️  Uploading '{os.path.basename(local_path)}' to '{remote_path}'...")
        sftp.put(local_path, remote_path)
        sftp.close()

        print(f"  ✅ Upload complete.")
        logging.info(f"Successfully uploaded {local_path} to {host}:{remote_path}")

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
        description="Upload a file to multiple hosts defined in a hosts file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("hosts_file", help="Path to the hosts file.")
    parser.add_argument("-s", "--source", required=True, help="Path to the local file to upload.")
    parser.add_argument("-d", "--dest", required=True, help="Remote path where the file will be saved.")

    args = parser.parse_args()

    if not os.path.exists(args.source):
        logging.critical(f"Source file not found: '{args.source}'. Aborting.")
        sys.exit(1)

    hosts = parse_hosts_file(args.hosts_file)
    if not hosts:
        logging.critical("No valid hosts found in the file. Exiting.")
        return

    for host_details in hosts:
        upload_file_to_host(host_details, args.source, args.dest)


if __name__ == "__main__":
    main()