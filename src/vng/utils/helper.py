from uuid import UUID


def validateUUID(uuid):
    try:
        UUID(uuid)
        return True
    except ValueError:
        return False
