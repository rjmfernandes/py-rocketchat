#!/usr/bin/env python
import string
from random import choice
from dotenv import dotenv_values
from pymongo import MongoClient
from datetime import datetime


def get_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(choice(characters) for i in range(length))


config = dotenv_values(".env")

database = MongoClient(config["DB_URI"])[config["RC_DB"]]
oldUser = config["OLD_USER"]
newUser = config["NEW_USER"]
rooms = []
roomsNewUserIsNot = []
roomsNewUserAlreadyBelongsTo = []

user = database["users"].find_one({"username": newUser})

roomsCursor = database["rocketchat_room"].find({"u.username": oldUser})
for room in roomsCursor:
    rooms.append(room)
    if room["_id"] in user["__rooms"]:
        roomsNewUserAlreadyBelongsTo.append(room)
    else:
        roomsNewUserIsNot.append(room)

print(f'1. Found {len(rooms)} rooms owned by user {oldUser}')

database["rocketchat_room"].update_many({"u.username": oldUser},
                                        {"$set": {"u": {"_id": user["_id"], "username": newUser}}})

print(f'2. Updated the owner of the rooms owned by {oldUser} to the new owner {newUser}')

print(f'3. Rooms owned by {oldUser} that new user {newUser} was not part of (size: {len(roomsNewUserIsNot)})')

for index, room in enumerate(roomsNewUserIsNot):
    print(f'  3.{index} Managing room {room["fname"]}')
    database["users"].update_one({"username": newUser}, {"$push": {"__rooms": room["_id"]}})
    print(f'    3.{index}.1 Added room {room["fname"]} to the new user {newUser} rooms')
    database["rocketchat_room"].update_one({"_id": room["_id"]}, {"$inc": {"usersCount": 1}})
    print(f'    3.{index}.2 Incremented in one the number of users for the room {room["name"]}')
    nowDate = datetime.utcnow()
    newMessage = {
        "_id": get_random_string(17),
        "t": "au",
        "rid": room["_id"],
        "ts": nowDate,
        "ms": newUser,
        "u": {
            "_id": user["_id"],
            "username": newUser
        },
        "groupable": False,
        "_updatedAt": nowDate
    }
    database["rocketchat_message"].insert_one(newMessage)
    print(f'    3.{index}.3 Sent message to room {room["name"]} about new user {newUser} added')
    database["rocketchat_room"].update_one({"_id": room["_id"]}, {"$inc": {"msgs": 1}})
    print(f'    3.{index}.4 Incremented room {room["fname"]} messages count')
    nowDate = datetime.utcnow()
    newSubscription = {
        "_id": get_random_string(24),
        "open": True,
        "alert": False,
        "unread": 0,
        "userMentions": 0,
        "groupMentions": 0,
        "ts": nowDate,
        "rid": room["_id"],
        "name": room["name"],
        "fname": room["fname"],
        "customFields": {},
        "t": room['t'],
        "u": {
            "_id": user["_id"],
            "username": newUser
        },
        "ls": nowDate,
        "_updatedAt": nowDate,
        "roles": [
            "owner"
        ]
    }
    database["rocketchat_subscription"].insert_one(newSubscription)
    print(f'    3.{index}.5 Registered subscription in room {room["name"]} for new user {newUser}')

print(
    f'4. Rooms owned by {oldUser} that new user {newUser} was part of (size: {len(roomsNewUserAlreadyBelongsTo)})')
for index, room in enumerate(roomsNewUserAlreadyBelongsTo):
    database["rocketchat_subscription"].update_one({"u.username": newUser, "rid": room["_id"]},
                                                  {"$set": {"roles": ["owner"]}})
    print(
        f'  4.{index} New user {newUser} role for room {room["name"]} set as owner')

database["rocketchat_subscription"].update_many({"u.username": oldUser, "roles": {"$in": ["owner"]}},
                                                {"$unset": {"roles": ""}})

print(
    f'5. Owner roles subscription for rooms for user {oldUser} removed')
