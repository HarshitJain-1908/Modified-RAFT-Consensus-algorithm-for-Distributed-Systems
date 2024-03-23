# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\x12\x04raft\"\x98\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x10\n\x08leaderId\x18\x02 \x01(\x05\x12\x14\n\x0cprevLogIndex\x18\x03 \x01(\x05\x12\x13\n\x0bprevLogTerm\x18\x04 \x01(\x05\x12\x1f\n\x07\x65ntries\x18\x05 \x03(\x0b\x32\x0e.raft.LogEntry\x12\x14\n\x0cleaderCommit\x18\x06 \x01(\x05\"k\n\x12\x41ppendEntriesReply\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x14\n\x0c\x63onflictTerm\x18\x03 \x01(\x05\x12 \n\x18\x66irstIndexOfConflictTerm\x18\x04 \x01(\x05\")\n\x08LogEntry\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07\x63ommand\x18\x02 \x01(\t\"b\n\x12RequestVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0b\x63\x61ndidateId\x18\x02 \x01(\x05\x12\x14\n\x0clastLogIndex\x18\x03 \x01(\x05\x12\x13\n\x0blastLogTerm\x18\x04 \x01(\x05\"5\n\x10RequestVoteReply\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0bvoteGranted\x18\x02 \x01(\x08\"\"\n\x0fServeClientArgs\x12\x0f\n\x07Request\x18\x01 \x01(\t\"C\n\x10ServeClientReply\x12\x0c\n\x04\x44\x61ta\x18\x01 \x01(\t\x12\x10\n\x08LeaderID\x18\x02 \x01(\t\x12\x0f\n\x07Success\x18\x03 \x01(\x08\x32\xd9\x01\n\x0bRaftService\x12G\n\rAppendEntries\x12\x1a.raft.AppendEntriesRequest\x1a\x18.raft.AppendEntriesReply\"\x00\x12\x41\n\x0bRequestVote\x12\x18.raft.RequestVoteRequest\x1a\x16.raft.RequestVoteReply\"\x00\x12>\n\x0bServeClient\x12\x15.raft.ServeClientArgs\x1a\x16.raft.ServeClientReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_APPENDENTRIESREQUEST']._serialized_start=21
  _globals['_APPENDENTRIESREQUEST']._serialized_end=173
  _globals['_APPENDENTRIESREPLY']._serialized_start=175
  _globals['_APPENDENTRIESREPLY']._serialized_end=282
  _globals['_LOGENTRY']._serialized_start=284
  _globals['_LOGENTRY']._serialized_end=325
  _globals['_REQUESTVOTEREQUEST']._serialized_start=327
  _globals['_REQUESTVOTEREQUEST']._serialized_end=425
  _globals['_REQUESTVOTEREPLY']._serialized_start=427
  _globals['_REQUESTVOTEREPLY']._serialized_end=480
  _globals['_SERVECLIENTARGS']._serialized_start=482
  _globals['_SERVECLIENTARGS']._serialized_end=516
  _globals['_SERVECLIENTREPLY']._serialized_start=518
  _globals['_SERVECLIENTREPLY']._serialized_end=585
  _globals['_RAFTSERVICE']._serialized_start=588
  _globals['_RAFTSERVICE']._serialized_end=805
# @@protoc_insertion_point(module_scope)
