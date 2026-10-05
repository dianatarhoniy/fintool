import threading

from modules.finding import Finding


class DoubleSpending():
    def __init__(self, client,auth,config):
        self.client = client
        self.auth = auth
        self.config = config
        self.results = []
        self.lock = threading.Lock()
    def send_transfer(self, sender, receiver, amount):
        response = self.client.post(self.config["path"], data={
            self.config["from_field"]: sender,
            self.config["to_field"]: receiver,
            self.config["amount_field"]: amount,
            self.config["submit_field"]: self.config["submit_value"]
        })
        with self.lock:
            if response.status_code == 200:
                self.results.append("SUCCESS")
            else:
                self.results.append("FAIL")

    def run(self, threads=10):
        print(f"Starting Double Spending detection with {threads} concurrent threads...")
        sender = self.config["sender"]
        receiver = self.config["receiver"]
        amount = self.config["amount"]
        self.results = []
        findings = []

        balance_before = self.auth.get_balance()
        if balance_before is None:
            print("[DOUBLE SPENDING] Could not read starting balance - aborting test.")
            return findings
        before = float(balance_before.replace("$", "").replace(",", "").strip())

        # Fire many transfers simultaneously
        thread_list = []
        for _ in range(threads):
            t = threading.Thread(target=self.send_transfer, args=(sender, receiver, amount))
            thread_list.append(t)

        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()

        balance_after = self.auth.get_balance()
        if balance_after is None:
            print("[DOUBLE SPENDING] Could not read balance - aborting test.")
            return findings

        after = float(balance_after.replace("$", "").replace(",", "").strip())

        delta = round(before - after, 2)
        expected = float(amount)
        successes = self.results.count("SUCCESS")

        print(f"\n[DOUBLE SPENDING] Analysis:")
        print(f"Threads fired       : {threads}")
        print(f"Requests succeeded  : {successes}/{threads}")
        print(f"Balance before      : {balance_before}")
        print(f"Balance after       : {balance_after}")
        print(f"Amount per transfer : ${amount}")
        print(f"Expected deduction  : ${expected} (1 transfer)")
        print(f"Actual deduction    : ${delta}")

        if delta > expected:
            times = round(delta / expected)
            print(f"\nVULNERABILITY DETECTED - Balance dropped {times}x the transfer amount!")
            print(f"Server processed {times} out of {threads} concurrent transfers.")
            findings.append(Finding(
                check="Double Spending",
                severity="HIGH",
                title="Race condition allows duplicate transfers",
                evidence=f"{threads} concurrent transfers of ${amount} caused a ${delta} deduction ({times}x expected)"
            ))
        else:
            print(f"\nSAFE - Balance only dropped once despite {threads} concurrent requests.")
            findings.append(Finding(
                check="Double Spending",
                severity="SAFE",
                title="No double-spending detected",
                evidence=f"Balance dropped ${delta} after {threads} concurrent transfers (expected ${expected})"
            ))
        return findings