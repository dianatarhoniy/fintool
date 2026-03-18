import subprocess
class EndpointDiscovery:
    def __init__(self,target):
        self.target = target
        self.wordlist = "/Users/diana/fintech-tool/wordlists/common.txt"

    def search(self):
        print("Searching for endpoints...")
        command = ["gobuster", "dir", "-u", self.target, "-w",self.wordlist,"-q"]
        subprocess.run(command)



