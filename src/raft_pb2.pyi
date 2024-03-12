from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServeClientArgs(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: str
    def __init__(self, request: _Optional[str] = ...) -> None: ...

class ServeClientReply(_message.Message):
    __slots__ = ("data", "leaderID", "success")
    DATA_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    data: str
    leaderID: str
    success: bool
    def __init__(self, data: _Optional[str] = ..., leaderID: _Optional[str] = ..., success: bool = ...) -> None: ...

class AppendEntryArgs(_message.Message):
    __slots__ = ("term", "leaderId", "prevLogIndex", "prevLogTerm", "entries", "leaderCommit", "leaseDuration")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    PREVLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    PREVLOGTERM_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    LEADERCOMMIT_FIELD_NUMBER: _ClassVar[int]
    LEASEDURATION_FIELD_NUMBER: _ClassVar[int]
    term: int
    leaderId: str
    prevLogIndex: int
    prevLogTerm: int
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    leaderCommit: int
    leaseDuration: int
    def __init__(self, term: _Optional[int] = ..., leaderId: _Optional[str] = ..., prevLogIndex: _Optional[int] = ..., prevLogTerm: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ..., leaderCommit: _Optional[int] = ..., leaseDuration: _Optional[int] = ...) -> None: ...

class AppendEntryReply(_message.Message):
    __slots__ = ("term", "success")
    TERM_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    term: int
    success: bool
    def __init__(self, term: _Optional[int] = ..., success: bool = ...) -> None: ...

class RequestVoteArgs(_message.Message):
    __slots__ = ("term", "candidateId", "lastLogIndex", "lastLogTerm")
    TERM_FIELD_NUMBER: _ClassVar[int]
    CANDIDATEID_FIELD_NUMBER: _ClassVar[int]
    LASTLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    LASTLOGTERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    candidateId: str
    lastLogIndex: int
    lastLogTerm: int
    def __init__(self, term: _Optional[int] = ..., candidateId: _Optional[str] = ..., lastLogIndex: _Optional[int] = ..., lastLogTerm: _Optional[int] = ...) -> None: ...

class RequestVoteReply(_message.Message):
    __slots__ = ("term", "voteGranted", "leaseDuration")
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTEGRANTED_FIELD_NUMBER: _ClassVar[int]
    LEASEDURATION_FIELD_NUMBER: _ClassVar[int]
    term: int
    voteGranted: bool
    leaseDuration: int
    def __init__(self, term: _Optional[int] = ..., voteGranted: bool = ..., leaseDuration: _Optional[int] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ("term", "command")
    TERM_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    term: int
    command: str
    def __init__(self, term: _Optional[int] = ..., command: _Optional[str] = ...) -> None: ...
