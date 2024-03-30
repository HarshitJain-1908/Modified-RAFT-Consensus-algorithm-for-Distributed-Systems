# Raft Consensus Algorithm with Leader Lease

This is a modified implementation of the Raft consensus algorithm with leader lease functionality. The code is written in Python and uses gRPC for communication between nodes. The implementation includes the following features:

- **Node Roles:** Nodes can be in one of three roles: Follower, Candidate, or Leader.
- **Leader Lease:** The leader has a lease duration, and if it does not renew the lease in time, a new leader election is triggered.
- **Log Replication:** Logs are replicated across the cluster, and committed entries are applied to the state machine.
- **RPC Communication:** Nodes communicate using gRPC for RequestVote, AppendEntries, and ServeClient RPCs.

### Overview
This project implements the Raft consensus algorithm with a leader lease modification. The system consists of multiple Raft nodes hosted on separate Virtual Machines (VMs) on Google Cloud, and a client that interacts with the Raft cluster to store and retrieve key-value pairs in a fault-tolerant manner. Communication between nodes and with clients is achieved using gRPC.

### Implementation Details
1. **Storage and Database Operations**
   - Each Raft node persists its logs, metadata, and a dump file for debugging purposes. Logs are stored in a human-readable format (e.g., .txt).
   - Logs only store WRITE operations and NO-OP operations, along with the term number.
   - Supported operations:
     - SET K V: Maps key K to value V.
     - GET K: Retrieves the latest committed value of key K.

2. **Client Interaction**
   - The client stores node IP addresses and ports, along with the current leader ID.
   - It sends GET/SET requests to the leader node, updating the leader ID in case of failure.
   - The client retries requests until receiving a SUCCESS reply from any node.

3. **Standard Raft RPCs**
   - Two RPCs are used: AppendEntry and RequestVote.
   - AppendEntry RPC includes the lease interval duration for leader lease modification.
   - RequestVoteReply includes the longest remaining duration of an old leader's lease.

4. **Election Functionalities**
   - Nodes maintain an election timer and listen for heartbeat or vote request events.
   - Election timeout is randomized to prevent simultaneous elections.
   - Nodes vote for a candidate based on specific conditions.
   - A new leader waits for the maximum of the old leader's lease timer before acquiring its own lease.

5. **Log Replication Functionalities**
   - Leader sends periodic heartbeats to all nodes, renewing its lease and propagating the lease duration.
   - Replication of log entries is done through AppendEntriesRPC, synchronizing follower logs with the leader's.
   - Nodes commit entries only when specific conditions are met.

6. **Committing Entries**
   - Leader commits an entry when a majority of nodes acknowledge appending the entry and when the entry belongs to the leader's term.
   - Followers commit entries using the LeaderCommit field in the AppendEntry RPC received in each heartbeat.

7. **Print Statements & Dump.txt**
   - Nodes print various statements for debugging purposes, including lease renewal, election timeouts, leader status changes, and committed entries.
   - Dump files follow a specific naming convention and contain detailed node state information.

### Running the System
1. **Node Setup**
   - Each node is hosted on a separate VM.
   - Install dependencies: Python, gRPC.
   - Clone the repository and navigate to the node directory.
   - Start the node using `python node.py <node_id> <cluster_nodes>`.

2. **Client Setup**
   - Install dependencies: Python, gRPC.
   - Clone the repository and navigate to the client directory.
   - Start the client using `python client.py --nodes <node_addresses>`.

3. **Testing and Debugging**
   - Use print statements and log files to debug the system.
   - Test the system under various failure scenarios (e.g., node crashes, network partitions) to ensure fault tolerance.

## Installation

To run the Raft consensus algorithm, you need Python3 installed. Additionally, install the required dependencies using pip:

```bash
pip install grpcio grpcio-tools
```

## Usage

1. Define the cluster nodes in the `cluster_nodes` list.
2. Create a `RaftNode` instance for each node in the cluster.
3. Call the `run` method on each `RaftNode` instance to start the node.

```python
cluster_nodes = ["localhost:5000", "localhost:5001", "localhost:5002"]
nodes = [RaftNode(get_id(node), cluster_nodes) for node in cluster_nodes]

for node in nodes:
    node.run()
```

## Example Usage

```python
# Setting a key-value pair
node.set_key_value("key", "value")

# Getting the value for a key
value = node.get_key_value("key")
print(value)
```
### Conclusion

This implementation of the Raft consensus algorithm with leader lease modification provides a robust and fault-tolerant distributed system for storing and retrieving key-value pairs. It ensures consistency, availability, and partition tolerance, making it suitable for use in distributed databases and systems requiring strong consistency guarantees.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.