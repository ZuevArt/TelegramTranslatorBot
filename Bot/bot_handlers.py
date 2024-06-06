from telethon import events, TelegramClient
from pydub import AudioSegment
from Translator.translator_class import Translate
from Bot import work_with_db
from Bot import db_for_languages
import aiofiles
import speech_recognition as sr
import os
from wit import Wit

wit_client = Wit('LPQ77ZJUAPTXNJVZKEVH4BXZQLHNQ7HN')

disable_commands = {}
conversation_state = {}


@events.register(events.NewMessage(pattern='(?i)/start'))
async def start_handler(event):
    if disable_commands.get(event.sender_id):
        await event.reply("This is a command. Please enter your text.")
        return

    client = event.client
    sender = await event.get_sender()
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



async def voice_to_text(event, client: TelegramClient):
    sender = await event.get_sender()
    SENDER = sender.id

    voice = event.message.media.document
    voice_file_path = await client.download_media(voice, file='voice.ogg')

    audio = AudioSegment.from_ogg(voice_file_path)
    audio = audio.set_channels(1)
    audio.export('voice.wav', format='wav')

    recognizer = sr.Recognizer()
    with sr.AudioFile('voice.wav') as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='en-US')
            await event.reply(f'Распознанный текст: {text}')
            state = conversation_state.get(SENDER)
            if state and state["stage"] == "input_text":
                state["message_for_translate"] = text
                state["text"] = text
                state["stage"] = "input_language"
                await client.send_message(SENDER, Translate.create_text_message())
        except sr.UnknownValueError:
            await event.reply('Не удалось распознать голос. Попробуйте еще раз.')
        except sr.RequestError as e:
            await event.reply(f'Ошибка сервиса распознавания: {e}')

        os.remove('voice.ogg')
        os.remove('voice.wav')


@events.register(events.NewMessage(pattern='(?i)/voice_translate'))
async def voice_translate_handler(event):
    if disable_commands.get(event.sender_id):
        await event.reply("This is a command. Please enter your text.")
        return
    client = event.client

    @client.on(events.NewMessage(func=lambda e: e.voice))
    async def handle_voice_message(event1):
        await voice_to_text(event1, client)


@events.register(events.NewMessage(pattern='(?i)/translate'))
async def translate_handler(event1):
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
            if given_text.lower().startswith("/"):
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
                    original_text_label = Translate('auto').translate_message("Your original text:", language_code)
                    translated_text_label = Translate('auto').translate_message("Your translated text:", language_code)

                    await client.send_message(SENDER, "Translated message:\n" + translated_message)

                    filename = f"translated_message_{sender_name}.txt"
                    async with aiofiles.open(filename, 'w') as f:
                        await f.write(
                            f"{original_text_label} {state['message_for_translate']}\n\n{translated_text_label} {translated_message}")
                        work_with_db.add_elements(sender, target_language, translated_message,
                                                  work_with_db.create_database())
                        db_for_languages.update_language_usage(SENDER, target_language, db_for_languages.create_usage_database())
                    await client.send_file(SENDER, filename)
                else:
                    await client.send_message(SENDER, translated_message)
                    work_with_db.add_last_message(SENDER, translated_message, work_with_db.create_database())
                del conversation_state[SENDER]
                disable_commands[SENDER] = False
            else:
                if not state.get("invalid_attempt", False):
                    await client.send_message(SENDER, "Invalid language code. Please try again.")
                    state["invalid_attempt"] = True
                    state["text"] = target_language


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
