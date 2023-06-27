class ClientError(Exception):
    """An error occurred on the client side"""

    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f"HTTP Client Error. Status code: {self.status_code}"


class NotFoundError(ClientError):
    """The server cannot find the requested resource"""

    pass


class TooManyRequests(ClientError):
    """The user has sent too many requests to the server in a given amount of time"""

    pass


class UnauthorizedError(ClientError):
    """The client request has not been completed because it lacks valid authentication credentials for the requested
    resource"""

    pass


class ServerError(Exception):
    """An error occurred on the server side"""

    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f"HTTP Server Error. Status code: {self.status_code}"
