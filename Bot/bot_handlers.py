from telethon import events
from telethon.tl.custom import Button
import os
from Translator.translator_class import Translate
import asyncio
from Bot import work_with_db
import Translator.speech_to_text


disable_commands = {}
conversation_state = {}

key_audio = [[Button.inline("{}".format("english"), "en-GB"), Button.inline("{}".format("russian"), "ru-RU")],
             [Button.inline("{}".format("german"), "de-DE"), Button.inline("{}".format("french"), "fr-FR")],
             [Button.inline("{}".format("italian"), "it-IT"), Button.inline("{}".format("spanish"), "es-ES")]]

key_target = [[Button.inline("{}".format("english"), "english"), Button.inline("{}".format("russian"), "russian")],
              [Button.inline("{}".format("german"), "german"), Button.inline("{}".format("french"), "french")],
              [Button.inline("{}".format("italian"), "italian"), Button.inline("{}".format("spanish"), "spanish")]]

def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)


@events.register(events.NewMessage(pattern='(?i)/start'))
async def start_handler(event):
    if disable_commands.get(event.sender_id):
        await event.reply("This is a command. Please enter your text.")
        return

    client = event.client
    sender = await event.get_sender()
    work_with_db.add_elements(sender, work_with_db.create_database())
    SENDER = sender.id
    text = "Hello"
    await client.send_message(SENDER, text, parse_mode="HTML")


@events.register(events.NewMessage(pattern='(?i)/help'))
async def help_handler(event):
    if disable_commands.get(event.sender_id):
        await event.reply("This is a command. Please enter your text.")
        return

    client = event.client
    sender = await event.get_sender()
    SENDER = sender.id
    text = ("Here you can find all commands\n"
            "\"<b>/start</b>\" -> Starting the Bot working\n"
            "\"<b>/translate</b>\" -> Calling a menu to translate your text\n"
            "\"<b>/stop</b>\" -> Stops working of the bot (only for developers)\n")
    await client.send_message(SENDER, text, parse_mode="HTML")


@events.register(events.NewMessage(pattern='(?i)/text_translate'))
async def text_translate_handler(event1):
    if disable_commands.get(event1.sender_id):
        await event1.reply("This is a command. Please enter your text.")
        return

    client = event1.client
    sender = await event1.get_sender()
    SENDER = sender.id
    sender_entity = await client.get_entity(SENDER)
    sender_name = sender_entity.first_name or "user"

    state = conversation_state.get(SENDER)
    if state is None:
        await client.send_message(SENDER, "Please enter your text")
        conversation_state[SENDER] = {"stage": "input_text"}
        disable_commands[SENDER] = True

    async with client.conversation(SENDER) as conv:
        state = conversation_state.get(SENDER)
        while True:
            try:
                text_message = await conv.wait_event(events.NewMessage(incoming=True, from_users=SENDER), timeout=60)
            except asyncio.TimeoutError:
                await client.send_message(SENDER, "Timeout: No response received. Please try again.")
                disable_commands[SENDER] = False
                del conversation_state[SENDER]
                return

            given_text = text_message.text
            if not given_text.startswith("/"):
                break
        state["message_for_translate"] = given_text
        text = "Available languages for translation"
        await conv.send_message(text, buttons=key_target, parse_mode='html')
        try:
            press = await asyncio.wait_for(conv.wait_event(press_event(SENDER)), timeout=300)
        except asyncio.TimeoutError:
            await client.send_message(SENDER, "Timeout: No response received. Please try again.")
            disable_commands[SENDER] = False
            del conversation_state[SENDER]
            return
        target_language = str(press.data.decode("utf-8"))
        translated_message = Translate('auto').translate_message(state["message_for_translate"], target_language)
        if len(translated_message) < 1000:
            await client.send_message(SENDER, "Translated message:\n" + translated_message)
        else:
            original_text_label = "Your original text: "
            translated_text_label = "Your translated text: "
            filename = f"translated_message_{sender_name}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(
                        f"{original_text_label} {state['message_for_translate']}\n\n{translated_text_label} {translated_message}")
                await client.send_file(SENDER, filename)
            except UnicodeEncodeError as e:
                await client.send_message(SENDER, f"UnicodeEncodeError: {e}")
            except Exception as e:
                await client.send_message(SENDER, f"An error occurred: {e}")
        disable_commands[SENDER] = False
        del conversation_state[SENDER]


@events.register(events.NewMessage(pattern='(?i)/voice_translate'))
async def voice_translate_handler(event):
    if disable_commands.get(event.sender_id):
        await event.reply("This is a command. Please enter your text.")
        return
    client = event.client
    sender = await event.get_sender()
    SENDER = sender.id
    await client.send_message(SENDER, "Please send me the voice message you want to translate.")
    disable_commands[SENDER] = True

    while True:
        async with client.conversation(SENDER) as conv:
            try:
                response = await conv.wait_event(events.NewMessage(incoming=True, from_users=SENDER), timeout=300)
            except asyncio.TimeoutError:
                await client.send_message(SENDER, "Timeout: No response received. Please try again.")
                disable_commands[SENDER] = False
                del conversation_state[SENDER]
                return
            if response.media and response.media.document.mime_type == 'audio/ogg':
                voice_message = await client.download_media(response.media.document, f'downloads/{SENDER}.ogg')
                print('Received voice message:', voice_message)
                wav_file_path = f'./downloads/{SENDER}.wav'
                Translator.speech_to_text.convert_ogg_to_wav(f'downloads/{SENDER}.ogg', wav_file_path)

                text = "Choose language of given audio file (will be removed in next patch)"
                await conv.send_message(text, buttons=key_audio, parse_mode='html')
                press = await conv.wait_event(press_event(SENDER))
                given_language = str(press.data.decode("utf-8"))

                transcription = Translator.speech_to_text.transcribe_audio_file(wav_file_path, given_language)
                await conv.send_message("Data from file\n" + transcription)

                text = "Available languages for translation"
                await conv.send_message(text, buttons=key_target, parse_mode='html')
                press = await conv.wait_event(press_event(SENDER))
                target_language = str(press.data.decode("utf-8"))
                translated_message = Translate('auto').translate_message(transcription, target_language)

                await conv.send_message("Translated message:\n" + translated_message)

                os.remove(f'./downloads/{SENDER}.ogg')
                os.remove(wav_file_path)
                disable_commands[SENDER] = False
                break
            else:
                await client.send_message(SENDER, "Please send a valid voice message.")


@events.register(events.NewMessage(pattern='(?i)/stop'))
async def stop_handler(event):
    if disable_commands.get(event.sender_id):
        await event.reply("This is a command. Please enter your text.")
        return

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
