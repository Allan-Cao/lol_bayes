class ClientError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f"HTTP Client Error. Status code: {self.status_code}"


class NotFoundError(ClientError):
    pass


class TooManyRequests(ClientError):
    pass


class UnauthorizedError(ClientError):
    pass


class ServerError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f"HTTP Server Error. Status code: {self.status_code}"
