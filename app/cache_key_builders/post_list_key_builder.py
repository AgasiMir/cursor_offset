from fastapi import Request, Response


def post_list_key_builder(
    func,
    namespace: str = "",
    *,
    request: Request | None = None,
    response: Response | None = None,
    **kwargs,
):
    query_params = request.query_params if request is not None else {}
    return ":".join(
        [
            namespace,
            repr(sorted(query_params.items())),
        ]
    )
