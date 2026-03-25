import tkinter as tk
from tkinter import ttk
import os
import subprocess
import psutil
import configparser as cp

VERSION = "1.3.0"
WINDOW_WIDE = 500
WINDOW_TALL = 250

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

def log_message(msg):
    log_text.config(state='normal')
    log_text.insert(tk.END, msg + "\n")
    log_text.config(state='disabled')
    log_text.see(tk.END)

def get_files(directory=TARGET_DIR):
    try:
        return sorted([f for f in os.listdir(directory) if f.endswith('.mdb')])
    except Exception as e:
        log_message(f"Error: Could not list files: {e}")
        return []

def update_files():
    files = get_files()
    file_combo['values'] = files
    log_message("File list updated.")

def change_customer_db(default=False):
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
        log_message(f"Config updated successfully for file: {new_file if not default else 'default database'}")
    except Exception as e:
        log_message(f"Error: Could not update config file: {e}")

def restart_process(process_name, process_path):
    try:
        for proc in psutil.process_iter(attrs=["name"]):
            if proc.info["name"] == process_name:
                proc.terminate()
                proc.wait(timeout=5)
                break
        subprocess.Popen([process_path], shell=True)
        log_message(f"Process '{process_name}' restarted successfully.")
    except Exception as e:
        log_message(f"Error: Could not restart process: {e}")

def ldb_cleanup():
    for f in os.listdir(TARGET_DIR):
        if f.endswith('.ldb'):
            try:
                os.remove(os.path.join(TARGET_DIR, f))
            except Exception as e:
                log_message(f"Could not delete {f}: {e}")
    log_message("LDB files cleaned up.")


# GUI setup
root = tk.Tk()
root.title(f"dbSwap v {VERSION}")
root.geometry(f"{WINDOW_WIDE}x{WINDOW_TALL}")
root.resizable(False, False)

tk.Label(root, text=f"Select a file from {TARGET_DIR}:").pack(pady=5)
files = get_files(TARGET_DIR)
file_combo = ttk.Combobox(root, values=files, width=60)
file_combo.pack(pady=3)
if files:
    file_combo.current(0)

button_frame_top    = tk.Frame(root)
button_frame_top.pack(pady=3)

button_frame_bottom = tk.Frame(root)
button_frame_bottom.pack(pady=3)

tk.Button(button_frame_top, text="Refresh DB list", command=update_files                            ).pack(side=tk.LEFT, padx=5, pady=0)
tk.Button(button_frame_top, text="Update config",   command=change_customer_db                      ).pack(side=tk.LEFT, padx=5, pady=0)
tk.Button(button_frame_top, text="Restore Default", command=lambda: change_customer_db(default=True)).pack(side=tk.LEFT, padx=5, pady=0)
tk.Button(button_frame_top, text="Clean LDB",       command=ldb_cleanup                             ).pack(side=tk.LEFT, padx=5, pady=0)

tk.Button(button_frame_bottom, text="Restart AccuServer", command=lambda: restart_process(AS_PROCESS_NAME, AS_PROCESS_PATH)).pack(side=tk.LEFT, padx=5)

# Log text box
log_text = tk.Text(root, height=6, width=70, state='disabled', wrap='word', bg='#f5f5f5')
log_text.pack(pady=10, padx=10)

root.mainloop()
