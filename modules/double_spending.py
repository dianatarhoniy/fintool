import threading
class DoubleSpending():
    def __init__(self, client,auth):
        self.client = client
        self.auth = auth
        self.results = []
    def send_transfer(self, sender, receiver, amount):
        pass

    def run(self):
        print("Starting Double Spending detection...")
        t1 = threading.Thread(target=self.send_transfer)
        t2 = threading.Thread(target=self.send_transfer)

        t1.start()
        t2.start()
        t1.join()
        t2.join()



# 1. login
# 2. get balance before
# 3. send transfer
# 4. send same transfer again
# 5. get balance after
# 6. compare and report
