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

    data = kwargs.get("kwargs")
    if not isinstance(data, dict):
        return f"{namespace}:"

    post_uuid = data.get("post_uuid")

    return f"{namespace}:{post_uuid}"
