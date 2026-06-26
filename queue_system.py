import asyncio

active_users = set()
MAX_USERS = 20

def add_user(user_id):
    if len(active_users) >= MAX_USERS:
        return False
    active_users.add(user_id)
    return True

def remove_user(user_id):
    active_users.discard(user_id)


def start_queue(loop=None):
    """
    SAFE START: avoids 'no running event loop'
    """

    if loop is None:
        loop = asyncio.get_event_loop()

    async def runner():
        while True:
            await asyncio.sleep(5)

    loop.create_task(runner())
