import subprocess
import os
import shutil
class EndpointDiscovery:
    def __init__(self,target,wordlist="wordlists/common.txt"):
        self.target = target
        self.wordlist = wordlist

    def search(self):
        print("Searching for endpoints...")
        if shutil.which("gobuster") is None:
            print(f"[SKIP] gobuster is not installed - skipping endpoint discovery")
            return
        if not os.path.exists(self.wordlist):
            print(f"[SKIP] Wordlist not found: {self.wordlist}")
            return
        command = ["gobuster", "dir", "-u", self.target, "-w",self.wordlist,"-q"]
        subprocess.run(command)



