import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import psutil
import configparser as cp

# Parse configs
try:
    config = cp.ConfigParser()
    config.read('config.ini')
except Exception:
    pass

# Change this to the directory you want to list files from
TARGET_DIR = "C:/AccuServer/custom_db"
TARGET_CFG = "C:/AccuServer/AccuServer.cfg"
SEARCH_TEXT = "AccuServerDataAccess.POSDataAccess"
AS_PROCESS_NAME = "AccuServer.exe"
AS_PROCESS_PATH = "C:/AccuServer/AccuServer.exe"


def get_files(directory=TARGET_DIR):
    """Return a list of files in the given directory."""
    try:
        return sorted(os.listdir(directory))
    except Exception as e:
        return
        messagebox.showerror("Error", f"Could not list files: {e}")
        return []

def update_files():
    files = get_files()
    file_combo['values'] = files


def find_files(base_dir, filename):
    """Search for files with a given name in all subdirectories.
    Returns a list of dicts with name, path, size, and modified date."""
    results = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f == filename:
                path = os.path.join(root, f)
                try:
                    size = os.path.getsize(path)
                    mtime = os.path.getmtime(path)
                    modified = datetime.datetime.fromtimestamp(mtime)
                except Exception:
                    size, modified = None, None
                results.append({
                    "name": f,
                    "path": path,
                    "size": size,
                    "modified": modified
                })
    return results
    

# File functions
def change_customer_db(default=False):
    """Open a config file, find a line containing SEARCH_TEXT, and replace it with a new line."""
    new_file = file_combo.get()
    if default:
        new_line = '<Module path=AccuPOS.mdb VerifyOrders=false backupPath=autoBackup ClearCustomersOnClosedSales=false dbDriver=JadoZoom>AccuServerDataAccess.POSDataAccess</Module>'
    else:
        new_line = f'<Module path=custom_db/{new_file} VerifyOrders=false backupPath=autoBackup ClearCustomersOnClosedSales=false dbDriver=JadoZoom>AccuServerDataAccess.POSDataAccess</Module>'
    try:
        with open(TARGET_CFG, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(TARGET_CFG, "w", encoding="utf-8") as f:
            for line in lines:
                if SEARCH_TEXT in line:
                    f.write(new_line + "\n")
                else:
                    f.write(line)
        messagebox.showinfo("Success", f"Line containing '{SEARCH_TEXT}' updated successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Could not update config file: {e}")


# Process functions
def restart_process(process_name, process_path):
    """Look for a Windows process by name and restart it."""
    try:
        # Kill process if running
        for proc in psutil.process_iter(attrs=["name"]):
            if proc.info["name"] == process_name:
                proc.terminate()
                proc.wait(timeout=5)
                break

        # Start process again
        subprocess.Popen([process_path], shell=True)
        messagebox.showinfo("Success", f"Process '{process_name}' restarted successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Could not restart process: {e}")


# GUI
root = tk.Tk()
root.title("Manager")
root.geometry("500x200")
root.resizable(False, False)

# File section
tk.Label(root, text=f"Select a file from {TARGET_DIR}:").pack(pady=5)
files = get_files(TARGET_DIR)
file_combo = ttk.Combobox(root, values=files, width=60)
file_combo.pack(pady=5)


if files:
    file_combo.current(0)



# Frame for buttons
button_frame = tk.Frame(root)
#button_frame['borderwidth'] = 1
#button_frame['relief'] = 'groove'
button_frame.pack(pady=10)

refresh_db_button = tk.Button(button_frame, text="Refresh DB list", command=update_files)
refresh_db_button.pack(side=tk.LEFT, padx=10)

update_cfg_button = tk.Button(button_frame, text="Update config", command=change_customer_db)
update_cfg_button.pack(side=tk.LEFT, padx=10)

restart_accuserver_button = tk.Button(button_frame, text="Restart AccuServer", command=lambda: restart_process(AS_PROCESS_NAME, AS_PROCESS_PATH))
restart_accuserver_button.pack(side=tk.LEFT, padx=10)

default_button = tk.Button(button_frame, text="Restore Default", command=lambda: change_customer_db(default=True))
default_button.pack(side=tk.RIGHT, padx=15)

root.mainloop()
