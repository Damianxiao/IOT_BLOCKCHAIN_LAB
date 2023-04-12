import threading
import time
import hashlib
import time

start_time = time.time()

class Node:
    def __init__(self, port, difficulty):
        self.port = port
        self.peers = []
        self.messages = []
        self.difficulty = difficulty
        self.shares = None
        self.nonce = 0
        
        # 创建cgroup并设置CPU限制
        cg_name = f"node{port}_cg"
        os.system(f"sudo cgcreate -g cpu:{cg_name}")
        os.system(f"sudo cgset -r cpu.cfs_quota_us={cpu_limit} {cg_name}")

    def add_peer(self, peer):
        if peer not in self.peers:
            self.peers.append(peer)

    def remove_peer(self, peer):
        if peer in self.peers:
            self.peers.remove(peer)

    def broadcast(self, message):
        for peer in self.peers:
            peer.receive(self, message)

    def receive(self, sender, message):
        self.messages.append((sender, message))

    def run(self):
        while True:
            # 模拟发送消息
            message = "node {}: shares {}".format(self.port, self.shares)
            self.broadcast(message)
            print("{} :{}".format(self.port, message))
            time.sleep(2)

    def calculate_shares(self, nonce):
        """
        Calculate the number of valid shares for a given nonce and difficulty level.
        """
        target = int(self.difficulty, 16)
        shares = 0
        while True:
            hash_result = hashlib.sha256(str(nonce).encode()).hexdigest()
            hash_int = int(hash_result, 16)
            if hash_int < target:
                shares += 1
            nonce += 1
            if nonce % 100000 == 0:
                continue
            if shares > 0 :
                self.shares = shares
                message = f"Node {self.port} has generated {shares} shares"
                self.broadcast(message) # 广播产生新的shares信息
            if time.time() - start_time >= 5: # 5秒内产生的share
                print(f"Node {self.port} Nonce: {nonce}, Shares: {shares}")
                print(f"hash_int={hash_int} target={target}")
                break
        return shares

    def evaluate_node_performance(self):
        os.system(f"sudo cgclassify -g cpu:node{self.port}_cg {os.getpid()}")
        nonce = 0
        shares = self.calculate_shares(nonce)
        print(f"Node {self.port} shares: {shares}")
        self.shares = shares
    
    def start_evaluation(self):
        thread = threading.Thread(target=self.evaluate_node_performance)
        thread.start()
            
if __name__ == "__main__":
    
    nodes = [
        {"id": 1, "port": 5000, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 50000},
        {"id": 2, "port": 5001, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 75000},
        {"id": 3, "port": 5002, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 25000},
        {"id": 4, "port": 5003, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 30000},
        {"id": 5, "port": 5004, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 40000},
        {"id": 6, "port": 5005, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 20000},
        {"id": 7, "port": 5006, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 15000},
        {"id": 8, "port": 5007, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 80000},
        {"id": 9, "port": 5008, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 60000},
        {"id": 10, "port": 5009, "difficulty": "000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "cpu_limit": 35000}
        ]

    node_objects = []
    for node in nodes:
        node_object = Node(node["port"], node["difficulty"])
        node_objects.append(node_object)

    # 将节点互相连接
    for node in node_objects:
        for other_node in node_objects:
            if node != other_node:
                node.add_peer(other_node)

    threads = []
    for node in node_objects:
        thread = threading.Thread(target=node.run)
        threads.append(thread)
        thread.start()
        node.start_evaluation()

    while True:
        time.sleep(1)
        # for node in node_objects:
            # print(f"Node {node.port} shares: {node.shares}")
