from telethon import events
from Translator.translator_class import Translate


@events.register(events.NewMessage(pattern='(?i)/start'))
async def start_handler(event):
    client = event.client
    sender = await event.get_sender()
    SENDER = sender.id
    text = "Hello"
    await client.send_message(SENDER, text, parse_mode="HTML")


@events.register(events.NewMessage(pattern='(?i)/help'))
async def help_handler(event):
    client = event.client
    sender = await event.get_sender()
    SENDER = sender.id
    text = "Here you can find all commands\n" +\
        "\"<b>/start</b>\" -> Starting the Bot working\n" +\
        "\"<b>/translate</b>\" -> Calling a menu to translate your text\n" + \
        "\"<b>/stop</b>\" -> Stops working of the bot (only for developers)\n"
    await client.send_message(SENDER, text, parse_mode="HTML")

conversation_state = {}


@events.register(events.NewMessage(pattern='(?i)/translate'))
async def translate_handler(event1):
    client = event1.client
    sender = await event1.get_sender()
    SENDER = sender.id
    state = conversation_state.get(SENDER)
    if state is None:
        await client.send_message(SENDER, "Please enter your text")
        conversation_state[SENDER] = {"stage": "input_text"}

    @client.on(events.NewMessage(from_users=SENDER))
    async def handle_message(event2):
        state = conversation_state.get(SENDER)
        if state is None:
            return
        if state.get("invalid_attempt", False):
            if event2.raw_text.lower() != state["text"].lower():
                state.pop("invalid_attempt")

        if state["stage"] == "input_text":
            given_text = event2.raw_text.strip()
            if given_text.lower() == "/translate":
                return
            await client.send_message(SENDER, "Your text is: " + given_text)
            await client.send_message(SENDER, Translate.create_text_message())
            state["message_for_translate"] = given_text
            state["text"] = given_text
            state["stage"] = "input_language"
        elif state["stage"] == "input_language":
            target_language = event2.raw_text.lower()
            if target_language == state["text"]:
                return
            if Translate.check_target_language(target_language):
                language_code = Translate.check_target_language(target_language)
                await client.send_message(SENDER, "Your target language is: " + target_language)
                translated_message = Translate('auto').translate_message(state["message_for_translate"], language_code)
                if translated_message != "Translation error":
                    await client.send_message(SENDER, "Translated message\n" + translated_message)
                else:
                    await client.send_message(SENDER, translated_message)
                del conversation_state[SENDER]
            else:
                if not state.get("invalid_attempt", False):
                    await client.send_message(SENDER, "Invalid language code. Please try again.")
                    state["invalid_attempt"] = True
                    state["text"] = target_language


@events.register(events.NewMessage(pattern='(?i)/stop'))
async def stop_handler(event):
    client = event.client
    sender = await event.get_sender()
    exit_id_list = [975757295, 662398876]
    SENDER = sender.id
    print(SENDER)
    if SENDER in exit_id_list:
        text = "Goodbye :)"
        await client.send_message(SENDER, text, parse_mode="HTML")
        await client.disconnect()
    else:
        text = "You don't have permission to do that"
        await client.send_message(SENDER, text, parse_mode="HTML")
