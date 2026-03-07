from uuid import uuid4


def generate_sentinel_id() -> str:
    return 'sent-' + str(uuid4())
