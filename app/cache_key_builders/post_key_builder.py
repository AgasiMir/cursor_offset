from fastapi import Request


def post_key_builder(
    func,
    namespace: str = "",
    request: Request | None = None,
    response=None,
    *args,
    **kwargs,
):
    """
    Генерирует предсказуемый ключ вида:
    fastapi-cache:post:<post_uuid>
    """

    item_id = None
    if request is not None:
        item_id = request.path_params.get("post_uuid")

    if item_id is None:
        item_id = kwargs.get("post_uuid") or (args[0] if args else None)

    return f"{namespace}:{item_id}"
