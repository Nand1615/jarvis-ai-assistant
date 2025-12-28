import os
import subprocess
from memory.context import set_context
import os

# command = how to open
# process = how to close
APPS = {
    "notepad": {
        "command": "notepad",
        "process": "notepad.exe"
    },
    "calculator": {
        "command": "calc",
        "process": "Calculator.exe"
    },
    "calc": {
        "command": "calc",
        "process": "Calculator.exe"
    },
    "vscode": {
        "command": r"C:\Users\Lenovo\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe"
    },
    "visual studio code": {
        "command": r"C:\Users\Lenovo\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe"
    },
    "virtual studio code": {
        "command": r"C:\Users\Lenovo\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe"
    }
}
