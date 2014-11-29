class SSDBError(Exception):
    pass


class ConnectionError(SSDBError):
    pass


class TimeoutError(SSDBError):
    pass


class ProtocalError(SSDBError):
    pass


class RequestError(ProtocalError):
    pass


class ResponseError(ProtocalError):
    pass


class ServerError(SSDBError):
    pass
