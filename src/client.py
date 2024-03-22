import grpc
import raft_pb2
import raft_pb2_grpc

import argparse

class RaftClient(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node_addresses):
        self.node_addresses = node_addresses
        self.current_leader_id = 0

    def set_leader_id(self, leader_id):
        self.current_leader_id = leader_id

    def get_leader_id(self):
        return self.current_leader_id

    def send_request_to_leader(self, request):
        if self.current_leader_id is None:
            return None, "No leader available"

        try:
            print("*******************")
            with grpc.insecure_channel(self.node_addresses[self.current_leader_id]) as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                print(request)
                # print(dir(stub))
                reply = stub.ServeClient(raft_pb2.ServeClientArgs(Request=request))
                print(reply.Data, reply.LeaderID, reply.Success)
                return reply.Data, reply.LeaderID, reply.Success
        except grpc.RpcError as e:
            print("*******************")
            print(e.details())
            return None, "Failed to reach leader", False

    def serve_client(self, request):
        while True:
            data, leader_id, success = self.send_request_to_leader(request)
            if success:
                return data
            else:
                self.set_leader_id(leader_id)

    def set_key_value(self, key, value):
        request = f"SET {key} {value}"
        return self.serve_client(request)

    def get_value(self, key):
        request = f"GET {key}"
        return self.serve_client(request)

    def no_op(self):
        request = "NO-OP"
        return self.serve_client(request)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Raft Client')
    parser.add_argument('--nodes', nargs='+', help='Node addresses in the format localhost:port')
    args = parser.parse_args()

    if not args.nodes:
        print("Please provide node addresses using the --nodes argument.")
        return

    node_addresses = {i: address for i, address in enumerate(args.nodes)}

    # Initialize the Raft client
    client = RaftClient(node_addresses)

    # Menu loop
    while True:
        print("\nMenu:")
        print("1. Set a key-value pair")
        print("2. Get a value by key")
        print("3. Perform a NO-OP operation")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            key = input("Enter the key: ")
            value = input("Enter the value: ")
            response = client.set_key_value(key, value)
            print("Response:", response)
        elif choice == '2':
            key = input("Enter the key: ")
            response = client.get_value(key)
            print("Response:", response)
        elif choice == '3':
            response = client.no_op()
            print("Response:", response)
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
