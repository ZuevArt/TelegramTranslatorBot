from googletrans import Translator


translator = Translator()


class Translate:
    languages = {
        "en": "english",
        "ru": "russian",
        "de": "german",
        "it": "italian",
        "es": "spanish",
        "fr": "french",
    }
    lang_codes = dict(map(reversed, languages.items()))

    def __init__(self, source_language):
        self.source_language = source_language
        self.translator = Translator()

    def translate_message(self, message, target_language):
        try:
            translated_message = self.translator.translate(message, src=self.source_language, dest=target_language).text
            return translated_message
        except Exception as e:
            return f"Translation error {str(e)}"

    @staticmethod
    def create_text_message():
        text = "Available languages for translation:\n"
        for code, lang in Translate.languages.items():
            text += f"{code}: {lang}\n"
        return text

    @staticmethod
    def check_target_language(target_language):
        if target_language in Translate.lang_codes:
            return Translate.lang_codes[target_language]
        else:
            return False
