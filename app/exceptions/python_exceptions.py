class PostException(Exception):
    detail = "Unknown Exception."

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class PostNotFoundException(PostException):
    detail = "Post Not Found."
