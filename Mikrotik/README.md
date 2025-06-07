# MikroTik Automation Toolkit

This project is a suite of Python scripts designed to automate the management of multiple MikroTik routers (or any SSH-enabled devices). It allows for executing commands and uploading files efficiently across any number of configured hosts.

The toolkit is built on the **DRY (Don't Repeat Yourself)** principle, using a shared module for common functionality to ensure the project is easy to maintain and extend.

## Features

-   **Centralized Host Management**: Configure all your hosts in a single, readable `hosts.ini` file.
-   **Modular Tools**:
    -   `mikro_manager.py`: Execute one or more commands on all hosts.
    -   `file_uploader.py`: Upload any local file to a specified destination on all hosts.
-   **Shared Codebase**: A `common.py` module handles host configuration parsing, eliminating code duplication and simplifying updates.
-   **Flexible Authentication**: Supports both SSH private key and password authentication on a per-host basis.
-   **Robust Logging**: Each script maintains its own log file (`mikro_manager.log`, `file_uploader.log`) for auditing and debugging.
-   **Legacy Device Support**: Includes the necessary fix to connect to older devices that require the `ssh-rsa` algorithm.

## Project Structure

For the toolkit to function correctly, your files must be in the same directory, like this:

```
/YourProjectDirectory/
├── common.py
├── mikro_manager.py
├── file_uploader.py
├── hosts.ini
├── commands.txt
└── README.md
```

## Prerequisites

-   Python 3.6+
-   `pip` (Python package installer)

## Installation

1.  **Place the files** (`common.py`, `mikro_manager.py`, `file_uploader.py`) in the same directory.

2.  **Install Dependencies**: The only dependency is `paramiko`. It's best practice to use a `requirements.txt` file.

    Create a file named `requirements.txt` with this content:
    ```
    paramiko
    ```

    Then run the installation command in your terminal:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The script uses a `hosts.ini` file to manage connection details.

### `hosts.ini` Format

Each line defines a host using space-separated **key-value pairs**. Lines starting with `#` or `;` are ignored.

-   **Required Keys:** `host=<DeviceName>`, `ip=<ip_address>`
-   **Optional Keys:** `port=<port>`, `user=<username>`
-   **Authentication (choose one):** `key=</path/to/key>`, `password=<secret>`

### Example `hosts.ini`

```ini
# --- MikroTik Hosts Configuration ---

# Connect using a private key (user defaults to 'root')
host=Router-HQ ip=192.168.1.1 port=2222 key=~/.ssh/id_rsa

# Connect using a password and a specific user
host=Router-Branch ip=10.0.20.1 user=admin password=SecretPassword123!
```

## Usage

Each script is run from the command line.

### 1. `mikro_manager.py` (Command Executor)

This script executes one or more commands on your list of hosts.

**Specify commands directly:**
```bash
python mikro_manager.py hosts.ini --command "/system identity print" "/ip address print"
```

**Specify commands from a file:**
Create a `commands.txt` file with one command per line, then run:
```bash
python mikro_manager.py hosts.ini --file commands.txt
```

### 2. `file_uploader.py` (File Uploader)

This script uploads a single local file to a specified destination on all hosts.

**Syntax:**
```bash
python file_uploader.py <hosts_file> --source <local_file> --dest <remote_path>
```

**Example:**
To upload your public key:
```bash
# On Windows
python file_uploader.py hosts.ini --source "C:\Users\YourUser\.ssh\id_rsa.pub" --dest "id_rsa.pub"

# On Linux/macOS
python file_uploader.py hosts.ini --source "~/.ssh/id_rsa.pub" --dest "id_rsa.pub"
```