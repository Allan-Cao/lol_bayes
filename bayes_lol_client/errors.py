class ClientError(Exception):
    """An error occurred on the client side"""
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f"HTTP Client Error. Status code: {self.status_code}"


class NotFoundError(ClientError):
    """The resource was not found"""
    pass


class TooManyRequests(ClientError):
    """There were too many requests to the API"""
    pass


class UnauthorizedError(ClientError):
    # TODO: this could be wrong
    """The user is unauthorized to access a resource in the API"""
    pass


class ServerError(Exception):
    """An error occurred on the server side"""
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f"HTTP Server Error. Status code: {self.status_code}"
