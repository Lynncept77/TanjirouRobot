from typing import Dict, Union

from pyrogram import filters

from Tanji.pyrogramee.pluginshelper import member_permissions

from Tanji.mongo import db

from Tanji import pbot as app

karmadb = db.karma

karma_positive_group = 3

karma_negative_group = 4

async def int_to_alpha(user_id: int) -> str:

    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

    text = ""

    user_id = str(user_id)

    for i in user_id:

        text += alphabet[int(i)]

    return text

async def alpha_to_int(user_id_alphabet: str) -> int:

    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

    user_id = ""

    for i in user_id_alphabet:

        index = alphabet.index(i)

        user_id += str(index)

    user_id = int(user_id)

    return user_id


async def is_karma_on(chat_id: int) -> bool:
    chat = karmadb.find_one({"chat_id_toggle": chat_id})
    if not chat:
        return True
    return False


async def karma_on(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if is_karma:
        return
    return  karmadb.delete_one({"chat_id_toggle": chat_id})


async def karma_off(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if not is_karma:
        return
    return  karmadb.insert_one({"chat_id_toggle": chat_id})


async def get_karmas_count() -> dict:
    chats = karmadb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {}
    chats_count = 0
    karmas_count = 0
    for chat in await chats.to_list(length=1000000):
        for i in chat["karma"]:
            karmas_count += chat["karma"][i]["karma"]
        chats_count += 1
    return {"chats_count": chats_count, "karmas_count": karmas_count}


async def user_global_karma(user_id) -> int:
    chats = karmadb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return 0
    total_karma = 0
    for chat in await chats.to_list(length=1000000):
        karma = await get_karma(chat["chat_id"], await int_to_alpha(user_id))
        if karma:
            if int(karma["karma"]) > 0:
                total_karma += int(karma["karma"])
    return total_karma


async def get_karmas(chat_id: int) -> Dict[str, int]:
    karma = karmadb.find_one({"chat_id": chat_id})
    if karma:
        karma = karma["karma"]
    else:
        karma = {}
    return karma


async def get_karma(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    karmas = await get_karmas(chat_id)
    if name in karmas:
        return karmas[name]


async def update_karma(chat_id: int, name: str, karma: dict):
    name = name.lower().strip()
    karmas = await get_karmas(chat_id)
    karmas[name] = karma
    karmadb.update_one({"chat_id": chat_id}, {"$set": {"karma": karmas}}, upsert=True)

_mod_name_ = "Karma"

_help_ = """[UPVOTE] - Use upvote keywords like "+", "+1", "thanks" etc to upvote a message.

[DOWNVOTE] - Use downvote keywords like "-", "-1", etc to downvote a message.

Reply to a message with /karma to check a user's karma

Send /karma without replying to any message to chek karma list of top 10 users

<i> Special Credits to WilliamButcherBot </i>"""

regex_upvote = r"^((?i)\+|\+\+|\+1|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍|OwO|ÒwÓ|Piro|op|noice|sugoi)$"

regex_downvote = r"^(\-|\-\-|\-1|👎|bhkk|nub|ÕwÕ|Nezuko is my waifu|geh|)$"

@app.on_message(

    filters.text

    & filters.group

    & filters.incoming

    & filters.reply

    & filters.regex(regex_upvote)

    & ~filters.via_bot

    & ~filters.bot

    & ~filters.edited,

    group=karma_positive_group,

)

async def upvote(_, message):

    if not await is_karma_on(message.chat.id):

        return

    try:

        if message.reply_to_message.from_user.id == message.from_user.id:

            return

    except:

        return

    chat_id = message.chat.id

    try:

        user_id = message.reply_to_message.from_user.id

    except:

        return

    user_mention = message.reply_to_message.from_user.mention

    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))

    if current_karma:

        current_karma = current_karma["karma"]

        karma = current_karma + 1

        new_karma = {"karma": karma}

        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)

    else:

        karma = 1

        new_karma = {"karma": karma}

        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)

    await message.reply_text(

        f"Incremented Karma of {user_mention} By 1 \nTotal Points: {karma}"

    )

@app.on_message(

    filters.text

    & filters.group

    & filters.incoming

    & filters.reply

    & filters.regex(regex_downvote)

    & ~filters.via_bot

    & ~filters.bot

    & ~filters.edited,

    group=karma_negative_group,

)

async def downvote(_, message):

    if not await is_karma_on(message.chat.id):

        return

    try:

        if message.reply_to_message.from_user.id == message.from_user.id:

            return

    except:

        return

    chat_id = message.chat.id

    try:

        user_id = message.reply_to_message.from_user.id

    except:

        return

    user_mention = message.reply_to_message.from_user.mention

    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))

    if current_karma:

        current_karma = current_karma["karma"]

        karma = current_karma - 1

        new_karma = {"karma": karma}

        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)

    else:

        karma = 1

        new_karma = {"karma": karma}

        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)

    await message.reply_text(

        f"Decremented Karma Of {user_mention} By 1 \nTotal Points: {karma}"

    )

@app.on_message(filters.command("karma") & filters.group)

async def karma(_, message):

    chat_id = message.chat.id

    if len(message.command) != 2:

        if not message.reply_to_message:

            karma = await get_karmas(chat_id)

            msg = f"**Karma list of {message.chat.title}:- **\n"

            limit = 0

            karma_dicc = {}

            for i in karma:

                user_id = await alpha_to_int(i)

                user_karma = karma[i]["karma"]

                karma_dicc[str(user_id)] = user_karma

                karma_arranged = dict(

                    sorted(karma_dicc.items(), key=lambda item: item[1], reverse=True)

                )

            for user_idd, karma_count in karma_arranged.items():

                if limit > 9:

                    break

                try:

                    user_name = (await app.get_users(int(user_idd))).username

                except Exception:

                    continue

                msg += f"{user_name} : `{karma_count}`\n"

                limit += 1

            await message.reply_text(msg)

        else:

            user_id = message.reply_to_message.from_user.id

            karma = await get_karma(chat_id, await int_to_alpha(user_id))

            if karma:

                karma = karma["karma"]

                await message.reply_text(f"**Total Points**: __{karma}__")

            else:

                karma = 0

                await message.reply_text(f"**Total Points**: __{karma}__")

        return

    status = message.text.split(None, 1)[1].strip()

    status = status.lower()

    chat_id = message.chat.id

    user_id = message.from_user.id

    permissions = await member_permissions(chat_id, user_id)

    if "can_change_info" not in permissions:

        await message.reply_text("You don't have enough permissions.")

        return

    if status == "on" or status == "ON":

        await karma_on(chat_id)

        await message.reply_text(

            f"Added Chat {chat_id} To Database. Karma will be enabled here"

        )

    elif status == "off" or status == "OFF":

        await karma_off(chat_id)

        await message.reply_text(

            f"Removed Chat {chat_id} To Database. Karma will be disabled here"

        )
