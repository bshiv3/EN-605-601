#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = set()


def state_event():
    return json.dumps({"type": "state", **STATE})


def users_event():
    totalUsers = str(len(USERS) - 1)
    return json.dumps({"type": "users", "count": len(USERS), "message": "User Added to game. " + totalUsers + " total User(s)"})


async def notify_message(message):
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def messages(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            action = data["action"]
            if action == "minus":
                STATE["value"] -= 1
                await notify_state()
            elif action == "plus":
                STATE["value"] += 1
                await notify_state()
            else:
                print("unsupported event: ", data)
                await notify_message(message)
    finally:
        # print(error)
        await unregister(websocket)


start_server = websockets.serve(messages, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
