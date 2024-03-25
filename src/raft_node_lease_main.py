import random
import time
import grpc
from concurrent import futures
import argparse
import signal
import sys
import os

import raft_pb2
import raft_pb2_grpc
# import raft_pb2_grpcaf
# import raft_pb2

# Raft node states
FOLLOWER = 0
CANDIDATE = 1
LEADER = 2

# Raft node roles
REGULAR = 0
BOOTSTRAP = 1

LEASE_DURATION = 10

def get_id(s):
    return int(s.split('localhost:')[1]) - 5000

class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node_id, cluster_nodes, node_role=REGULAR):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.node_role = node_role
        

        self.current_term = 0
        self.voted_for = None
        self.log = []

        self.commit_index = -1
        self.last_applied = 0

        self.state = FOLLOWER
        self.leader_id = None
        
        # self.leader_address = None
        self.election_deadline = None
        self.heartbeat_timeout = None
        self.reset_election_timeout()
        
        self.lease_timeout = None
        self.max_old_leader_lease = 0

        
        LOGS_DIR = f"logs_node_{self.node_id}"
        self.logs_dir = LOGS_DIR.format(node_id=node_id)
        self.load_logs()

        self.next_index = {}
        self.match_index = {}
        for node in cluster_nodes:
            self.next_index[node] = 0
            self.match_index[node] = 0
            
    def load_logs(self):
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        log_file = os.path.join(self.logs_dir, "logs.txt")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                for line in f:
                    term, command = line.strip().split(" ", 1)
                    log_entry = raft_pb2.LogEntry()
                    log_entry.term = int(term)
                    log_entry.command = command
                    self.log.append(log_entry)
        else:
            self.log = []


        metadata_file = os.path.join(self.logs_dir, "metadata.txt")

        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                metadata = f.readline().strip().split()
                self.commit_index = int(metadata[0])-1
                self.current_term = int(metadata[1])
                self.voted_for = int(metadata[2])
        else:
            self.commit_length = 0
            self.current_term = 0
            self.voted_for = None

        dump_file = os.path.join(self.logs_dir, "dump.txt")

    def save_logs(self):
        log_file = os.path.join(self.logs_dir, "logs.txt")
        metadata_file = os.path.join(self.logs_dir, "metadata.txt")

        with open(log_file, "w") as f:
            for entry in self.log:
                f.write(f"{entry.term} {entry.command}\n")

        with open(metadata_file, "w") as f:
            f.write(f"{self.commit_index+1} {self.current_term} {self.voted_for}")

    def append_log_entry(self,entry):
        log_entry = raft_pb2.LogEntry()
        log_entry.term = self.current_term
        log_entry.command = entry
        self.log.append(log_entry)
        self.save_logs()

    def set_key_value(self, key, value):
        entry = f"SET {key} {value}"
        self.append_log_entry(entry)

    def get_key_value(self, key):
        print("hi2")
        print(self.log)
        for i in reversed(self.log[:self.commit_index+1]):
            print(i.term,i.command)
            if i.command.startswith(f"SET {key}"):
                return i.command.split()[2]
        return ""

    def ServeClient(self, request, context):
        print("Request",request)  
        command = request.Request.split()
        print("Command",command)
        
        if self.node_id != self.leader_id:
            return raft_pb2.ServeClientReply(
                Data="I am not the leader",
                LeaderID=str(self.leader_id),
                Success=False
            )
        
        # print("Key Value",key, value)
        if command[0] == "SET":
            key, value = command[1], command[2]
            print("set called")
            self.set_key_value(key, value)
            return raft_pb2.ServeClientReply(
                Data="SUCCESS",
                LeaderID=str(self.leader_id),
                Success=True
            )
        elif command[0] == "GET":
            key = command[1]
            print("hi")
            value = self.get_key_value(key)
            print("hi3")
            return raft_pb2.ServeClientReply(
                Data=value,
                LeaderID=str(self.leader_id),
                Success=True
            )
        else:
            return raft_pb2.ServeClientReply(
                Data="Invalid command",
                LeaderID=str(self.leader_id),
                Success=False
            )
        
    def reset_election_timeout(self):
        self.election_deadline = time.time() + random.uniform(5, 10)
        self.heartbeat_timeout = time.time() + 3

    def run(self):
        while True:
            if self.state == FOLLOWER:
                self.follower_routine()
            elif self.state == CANDIDATE:
                self.become_candidate()
            elif self.state == LEADER:
                self.leader_routine()

    def follower_routine(self):
        if time.time() >= self.election_deadline:
            print(f"Node {self.node_id}: Election timeout, becoming candidate from follower at time: {time.time()}")
            self.become_candidate()
            return

        # if self.leader_id is not None:
        #     if time.time() >= self.heartbeat_timeout:
        #         print(f"Node {self.node_id}: Heartbeat timeout, becoming candidate")
        #         print(self.heartbeat_timeout)
        #         self.become_candidate()
        #         return
            
            
    def candidate_routine(self):
        
        self.state = CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.leader_id = None
        self.reset_election_timeout()
        self.max_old_leader_lease = 0

        print(f"Node {self.node_id}: Became candidate for term {self.current_term}")

        votes = 1
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1].term if self.log else 0
        print("hi2")
        #
        # time.sleep(random.uniform(0.05, 0.1))

        vote_requests_sent = 0
        for node in self.cluster_nodes:
            if get_id(node) != self.node_id:
                request = raft_pb2.RequestVoteRequest(
                    term=self.current_term,
                    candidateId=self.node_id,
                    lastLogIndex=last_log_index,
                    lastLogTerm=last_log_term
                )
                try:
                    reply = self.request_vote(node, request)
                    vote_requests_sent += 1
                    if reply.voteGranted:
                        votes += 1
                        print(f"Node {self.node_id}: Received vote from {node}")
                        self.max_old_leader_lease = max(self.max_old_leader_lease, reply.oldLeaderLeaseDuration)
                        if votes > len(self.cluster_nodes) // 2:
                            print(f"Node {self.node_id}: Received majority votes, becoming leader")
                            self.become_leader()
                            return
                except grpc.RpcError:
                    vote_requests_sent += 1
                    print(f"Node {self.node_id}: Failed to send RequestVote to {node}, retrying later")

        # If no leader was elected and all vote requests were sent, check for election timeout
        while time.time() < self.election_deadline:
            print("hi")
            pass
        
        if vote_requests_sent == len(self.cluster_nodes) - 1:
            if time.time() >= self.election_deadline:
                print(f"Node {self.node_id}: Election timeout, starting new election at time: {time.time()}")
                self.become_candidate()



    def become_candidate(self):
        self.state = CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.leader_id = None
        self.reset_election_timeout()

        print(f"Node {self.node_id}: Became candidate for term {self.current_term} at time {time.time()}")

        votes = 1
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1].term if self.log else 0

        # time.sleep(random.uniform(0.05, 0.1))

        vote_requests_sent = 0
        for node in self.cluster_nodes:
            if get_id(node) != self.node_id:
                request = raft_pb2.RequestVoteRequest(
                    term=self.current_term,
                    candidateId=self.node_id,
                    lastLogIndex=last_log_index,
                    lastLogTerm=last_log_term
                )
                try:
                    reply = self.request_vote(node, request)
                    vote_requests_sent += 1
                    if reply.voteGranted:
                        votes += 1
                        print(f"Node {self.node_id}: Received vote from {node}")
                        if votes > len(self.cluster_nodes) // 2:
                            print(f"Node {self.node_id}: Received majority votes, becoming leader")
                            self.become_leader()
                            return
                except grpc.RpcError as e:
                    vote_requests_sent += 1
                    print(f"Node {self.node_id}: Failed to send RequestVote to {node}, retrying later")
                    

        # If no leader was elected and all vote requests were sent, check for election timeout
        while time.time() < self.election_deadline:
            pass
        
        if vote_requests_sent == len(self.cluster_nodes) - 1:
            if time.time() >= self.election_deadline:
                print(f"Node {self.node_id}: Election timeout, starting new election at time {time.time()}")
                self.become_candidate()

    def request_vote(self, node, request):
        with grpc.insecure_channel(node) as channel:
            stub = raft_pb2_grpc.RaftServiceStub(channel)
            return stub.RequestVote(request)

    def become_leader(self):
        self.state = LEADER
        self.leader_id = self.node_id
        # self.leader_address = f'localhost:{self.node_id + 5000}'
        self.reset_election_timeout()
        self.lease_timeout = time.time() + max(self.max_old_leader_lease, LEASE_DURATION)

        print(f"Node {self.node_id}: Became leader for term {self.current_term}")
        print(f"New Leader waiting for Old Leader Lease to timeout at time {self.lease_timeout}")

        for node in self.cluster_nodes:
            self.next_index[node] = len(self.log)
            self.match_index[node] = 0
        self.log.append(raft_pb2.LogEntry(term=self.current_term, command="NO-OP"))
        self.broadcast_append_entries(lease_duration=LEASE_DURATION)

    def broadcast_append_entries(self, lease_duration=None):
        for node in self.cluster_nodes:
            if get_id(node) != self.node_id:
                self.send_append_entries(node, lease_duration)

    def send_append_entries(self, node, lease_duration=None):
        prev_log_index = self.next_index[node] - 1
        prev_log_term = self.log[prev_log_index].term if prev_log_index >= 0 else 0
        entries = self.log[self.next_index[node]:]

        request = raft_pb2.AppendEntriesRequest(
            term=self.current_term,
            leaderId=self.node_id,
            prevLogIndex=prev_log_index,
            prevLogTerm=prev_log_term,
            entries=entries,
            leaderCommit=self.commit_index,
            leaseDuration=lease_duration
        )

        try:
            print(f"Sending to node {node} at time {time.time()}")
            reply = self.append_entries(node, request)
            print("Sent")
            self.handle_append_entries_response(node, reply)
        except grpc.RpcError:
            print(f"Node {self.node_id}: Failed to send AppendEntries to {node}, decrementing next index at time {time.time()}")
            self.next_index[node] -= 1

    def append_entries(self, node, request):
        with grpc.insecure_channel(node, options= [('grpc.enable_retries', False)]) as channel:
            stub = raft_pb2_grpc.RaftServiceStub(channel)
            return stub.AppendEntries(request)

    def handle_append_entries_response(self, node, reply):
        if reply.success:
            self.match_index[node] = len(self.log) - 1
            #print(f"next_index{node} = {self.next_index[node]}; len(self.log) = {len(self.log)}, time: {time.time()}")
            self.next_index[node] = len(self.log)
            rep = 1
            for peer in self.cluster_nodes:
                if peer != self.node_id:
                    if self.match_index[peer] == len(self.log) - 1:
                        rep += 1
                if rep > len(self.cluster_nodes) // 2:
                    self.lease_timeout = time.time() + LEASE_DURATION
                    print("Actually Renewing lease")
                    break
            

            committed_entries = []
            for i in range(self.commit_index + 1, len(self.log)):
                if self.log[i].term == self.current_term:
                    replicated = 1
                    for peer in self.cluster_nodes:
                        if peer != self.node_id:
                            if self.match_index[peer] >= i:
                                replicated += 1
                    if replicated > len(self.cluster_nodes) // 2:
                        self.commit_index = i
                        committed_entries.append(self.log[i])
                        self.save_logs()

            if committed_entries:
                print(f"Node {self.node_id}: Committed entries up to index {self.commit_index}")

            self.apply_committed_entries(committed_entries)

        else:
            if reply.conflictTerm != -1:
                print(f"Node {self.node_id}: Received conflictTerm {reply.conflictTerm} from {node}, setting next index to {reply.firstIndexOfConflictTerm}")
                self.next_index[node] = reply.firstIndexOfConflictTerm
            else:
                print(f"Node {self.node_id}: Received unsuccessful AppendEntries reply from {node}, decrementing next index")
                self.next_index[node] -= 1

    def apply_committed_entries(self, entries):
        for entry in entries:
            self.last_applied += 1
            print(f"Node {self.node_id}: Applied entry with term {entry.term} and command {entry.command}")
            # Apply the committed entry to the state machine

    def leader_routine(self):
        if time.time() >= self.election_deadline:
            print(f"Node {self.node_id}: Election timeout, becoming follower")
            self.become_follower()
            return

        if time.time() >= self.heartbeat_timeout:
            print(f"Node {self.node_id}: Sending heartbeat to cluster")
            self.reset_election_timeout()
            self.broadcast_append_entries(lease_duration=LEASE_DURATION)
            
            self.heartbeat_timeout = time.time() + 1
            
        if time.time() >= self.lease_timeout:
            print(f"Leader {self.node_id} lease renewal failed. Stepping Down.")
            self.become_follower()
            

    def become_follower(self):
        self.state = FOLLOWER
        self.leader_id = None
        self.reset_election_timeout()

    def AppendEntries(self, request, context):
        # called on follower
        if request.term < self.current_term:
            print(f"Node {self.node_id}: Received AppendEntries request with stale term {request.term}, rejecting")
            return raft_pb2.AppendEntriesReply(
                term=self.current_term,
                success=False,
                conflictTerm=-1,
                firstIndexOfConflictTerm=-1
            )

        self.current_term = request.term
        self.leader_id = request.leaderId
        

        if self.state != FOLLOWER:
            print(f"Node {self.node_id}: Received AppendEntries request from new leader {request.leaderId}, becoming follower")
            self.become_follower()

        self.reset_election_timeout()
        

        prev_log_index = request.prevLogIndex
        prev_log_term = self.log[prev_log_index].term if prev_log_index >= 0 else 0
        #print("prev_log_index", prev_log_index, 'len(self.log)', len(self.log), "time", time.time())

        if prev_log_term != request.prevLogTerm:
            conflict_term = self.log[prev_log_index].term if prev_log_index >= 0 else -1
            first_index = prev_log_index
            while first_index >= 0 and self.log[first_index].term == conflict_term:
                first_index -= 1
            first_index += 1
            # first_index: index of the first log entry in the conflicting term
            print(f"Node {self.node_id}: Received conflicting entries from leader, sending conflict term {conflict_term} and first index {first_index}")

            return raft_pb2.AppendEntriesReply(
                term=self.current_term,
                success=False,
                conflictTerm=conflict_term,
                firstIndexOfConflictTerm=first_index
            )

        self.log = self.log[:prev_log_index + 1] # for deleting
        self.log.extend(request.entries) # for appending new entries
        self.commit_index = min(request.leaderCommit, len(self.log) - 1)

        committed_entries = []
        for i in range(self.last_applied + 1, self.commit_index + 1):
            committed_entries.append(self.log[i])

        if committed_entries:
            print(f"Node {self.node_id}: Committed entries up to index {self.commit_index}")

        self.apply_committed_entries(committed_entries)
        self.save_logs()
        print(f"Node {self.node_id}: Appended entries from leader {request.leaderId}")

        if request.leaseDuration is not None:
            self.lease_timeout = time.time() + request.leaseDuration


        return raft_pb2.AppendEntriesReply(
            term=self.current_term,
            success=True,
            conflictTerm=-1,
            firstIndexOfConflictTerm=-1
        )

    def RequestVote(self, request, context):
        print(f"received request vote from node {request.candidateId} at time {time.time()}")
        if request.term < self.current_term:
            print(f"Node {self.node_id}: Received RequestVote request with stale term {request.term}, rejecting")
            return raft_pb2.RequestVoteReply(
                term=self.current_term,
                voteGranted=False,
                oldLeaderLeaseDuration=0
            )
            
        if request.term > self.current_term:
            self.current_term = request.term
            self.voted_for = None
            self.state = FOLLOWER

        if self.voted_for is None or self.voted_for == request.candidateId:
            print(f"hi {request.candidateId}")
            last_log_index = len(self.log) - 1
            last_log_term = self.log[-1].term if self.log else 0
            print(request.lastLogTerm, request.lastLogIndex, last_log_term, last_log_index)
            if request.lastLogTerm > last_log_term or \
                    (request.lastLogTerm == last_log_term and request.lastLogIndex >= last_log_index):
                # Tie-breaker rule: If log terms and indices are the same, vote for the candidate with the higher ID
                #if request.lastLogTerm == last_log_term and request.lastLogIndex == last_log_index:
                if request.candidateId > self.node_id:
                    self.current_term = request.term
                    self.voted_for = request.candidateId
                    self.reset_election_timeout()
                    print(f"Node {self.node_id}: Granted vote to candidate {request.candidateId} for term {request.term} (tie-breaker)")
                    return raft_pb2.RequestVoteReply(
                        term=self.current_term,
                        voteGranted=True,
                        oldLeaderLeaseDuration=self.lease_timeout - time.time() if self.state == FOLLOWER and self.lease_timeout is not None else 0
                    )
                else:
                    self.current_term = request.term
                    self.voted_for = request.candidateId
                    self.reset_election_timeout()
                    print(f"Node {self.node_id}: Granted vote to candidate {request.candidateId} for term {request.term}")
                    return raft_pb2.RequestVoteReply(
                        term=self.current_term,
                        voteGranted=True,
                        oldLeaderLeaseDuration=self.lease_timeout - time.time() if self.state == FOLLOWER and self.lease_timeout is not None else 0
                    )
                    
        print(f"Node {self.node_id}: Rejected vote request from candidate {request.candidateId} for term {request.term} at time {time.time()}")
        #print(f"Node {self.node_id}: Last log term: {last_log_term}, last log index: {last_log_index}")
        print(f"Candidate's log term, log index {request.lastLogTerm}, {request.lastLogIndex}")
        print(f"{self.voted_for} ")
        return raft_pb2.RequestVoteReply(
            term=self.current_term,
            voteGranted=False,
            oldLeaderLeaseDuration=0
        )

def serve(node_id, cluster_nodes):
    node = RaftNode(node_id, cluster_nodes)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(node, server)
    server.add_insecure_port(f'[::]:{node_id + 5000}')
    print(f"Node {node_id}: Starting server on port {node_id + 5000}")
    server.start()

    try:
        node.run()
    except KeyboardInterrupt:
        server.stop(0)

    server.wait_for_termination()

def signal_handler(sig, frame):
    print("Received SIGINT signal, stopping servers...")
    for server in servers:
        server.stop(0)
    print("Servers stopped.")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    servers = []

    parser = argparse.ArgumentParser(description='Raft Node')
    parser.add_argument('node_id', type=int, help='Node ID')
    parser.add_argument('cluster_nodes', nargs='+', help='Cluster node addresses')
    args = parser.parse_args()

    all_nodes = [int(i.split('localhost:')[1]) - 5000 for i in args.cluster_nodes]
    serve(args.node_id, args.cluster_nodes)
