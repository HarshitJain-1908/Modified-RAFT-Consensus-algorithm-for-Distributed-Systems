import grpc
from concurrent import futures
import time
import raft_pb2
import raft_pb2_grpc
import random

class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self):
        self.state = 'follower'  # 'follower', 'candidate', 'leader'
        self.currentTerm = 0
        self.votedFor = None
        self.log = []
        self.commitIndex = 0
        self.lastApplied = 0
        self.electionTimeout = random.uniform(5, 10)  # Randomized election timeout in seconds

    def election_timer(self):
        # This function should be run in a separate thread
        while True:
            time.sleep(self.electionTimeout)
            if self.state == 'follower' or self.state == 'candidate':
                self.start_election()

    def start_election(self):
        self.state = 'candidate'
        self.currentTerm += 1
        self.votedFor = self.node_id  # Assume self.node_id is the node's unique ID
        # Reset election timer
        self.electionTimeout = random.uniform(5, 10)
        # Send RequestVote RPCs to all other servers
        # This part requires asynchronous RPC calls and handling responses

    def send_heartbeats(self):
        # This function should be run in a separate thread when the node is the leader
        while self.state == 'leader':
            # Prepare AppendEntryArgs message
            # Send AppendEntry RPCs to all followers
            # Wait for a short period (e.g., 1 second) before sending the next heartbeat
            time.sleep(1)

    def RequestVote(self, request, context):
        with self.state_lock:  # Assuming self.state_lock is a threading.Lock for thread-safe state access
            if request.term < self.currentTerm:
                # The requesting candidate is from an outdated term
                return raft_pb2.RequestVoteReply(term=self.currentTerm, voteGranted=False)
            if request.term > self.currentTerm or self.votedFor is None or self.votedFor == request.candidateId:
                # Update current term if the request is from a newer term
                self.currentTerm = request.term
                self.votedFor = request.candidateId
                self.reset_election_timer()  # Reset the election timer as we've heard from a candidate
                return raft_pb2.RequestVoteReply(term=self.currentTerm, voteGranted=True)
            else:
                return raft_pb2.RequestVoteReply(term=self.currentTerm, voteGranted=False)

    def AppendEntry(self, request, context):
        with self.state_lock:  # Ensure thread-safe access to the state
            if request.term < self.currentTerm:
                # The request is from an old term; ignore it
                return raft_pb2.AppendEntryReply(term=self.currentTerm, success=False)
            # Reset the election timer on receiving a heartbeat or log entry
            self.reset_election_timer()
            if request.term > self.currentTerm:
                # Update to the newer term
                self.currentTerm = request.term
                self.state = 'follower'
            self.votedFor = None  # Reset votedFor since we've acknowledged a leader in the current term

            # Process the log entries replication here. This involves:
            # 1. Checking if we have an entry at prevLogIndex whose term matches prevLogTerm
            # 2. If so, appending any new entries not already in the log
            # 3. If an existing entry conflicts with a new one (same index but different terms),
            #    delete the existing entry and all that follow it
            # 4. Set commitIndex = min(leaderCommit, index of last new entry)

            # This example does not detail log replication for brevity
            # Assume success for now
            return raft_pb2.AppendEntryReply(term=self.currentTerm, success=True)


    def ServeClient(self, request, context):
        if self.state != 'leader':
            # Redirect client to the current leader if known
            return raft_pb2.ServeClientReply(leaderID=self.leaderID, success=False)
        else:
            if request.type == 'SET':
                # Append the request to the leader's log
                # Replicate the log entry using AppendEntry RPCs
                # Respond to the client after successful replication
                return raft_pb2.ServeClientReply(data='OK', leaderID=self.node_id, success=True)
            elif request.type == 'GET':
                # Serve the read request directly if the leader lease is valid
                # This would involve checking the current time against the lease expiration time
                return raft_pb2.ServeClientReply(data=value, leaderID=self.node_id, success=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(RaftNode(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()