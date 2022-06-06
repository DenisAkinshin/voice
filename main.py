import webbrowser
import  speech_recognition
from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
import wave # создание и чтение аудиофайлов формата wav
import os
import json  # работа с json-файлами и json-строками
import pyttsx3



#Создае ассистента

class VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    global assistant
    global ttsEngine
    """
    Установка голоса по умолчанию (индекс может меняться в
    зависимости от настроек операционной системы)
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            # Microsoft Zira Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            # Microsoft David Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        # Microsoft Irina Desktop - Russian
        ttsEngine.setProperty("voice", voices[0].id)



def play_voice_assistant_speech(text_to_speech):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()

#Создадим функцию для записи и распознавания речи
def record_and_recognize_audio(*args:tuple) :
    """
       Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""
        #регулирвоание уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)
        try :
            print('Listening...')
            audio = recognizer.listen(microphone,5,5) #Здесь мы захватываем звук с микрофона

            with open("microphone-results.wav",'wb') as file:
                file.write(audio.get_wav_data())
        except speech_recognition.WaitTimeoutError:
            print('Can you check if your microphone is on, please?')
            return

        # использование online-распознавания через Google
        try:
            print('Started recognition')
            recognized_data = recognizer.recognize_google(audio, language='ru').lower() #Расшифровываем наш аудио-файл
        except speech_recognition.UnknownValueError :
            pass

        # в случае проблем с доступом в Интернет происходит выброс ошибки
        except speech_recognition.RequestError :
            print('Check your intenet connetion, please')
            recognized_data = use_offline_recognition()

        return recognized_data


#Создадим функцию для офлайн-распозания речи
def use_offline_recognition() :
    """
       Переключение на оффлайн-распознавание речи
       :return: распознанная фраза
    """
    recognized_data = " "

    try :
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.22"):
            print("Please download the model from:\n"
                  "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1)

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-ru-0.22")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение данных распознанного текста из JSON-строки
                # (чтобы можно было выдать по ней ответ)
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except :
            print("Sorry, speech service is unavailable. Try again later")
    return recognized_data



#Функция для обработки словаря

def execute_command_with_name(command_name: str, *args: list):
    """
        Выполнение заданной пользователем команды с дополнительными аргументами
        :param command_name: название команды
        :param args: аргументы, которые будут переданы в функцию
        :return:
    """
    print(*args)
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else :
            pass


#Команда поиска видео в ютубе
def search_video_yuotube(*args:tuple) : #Эта запись обозначает, что сюда можно передать множетсво элементов, они будут все добавлены в кортедж
    """
       Поиск видео на YouTube с автоматическим открытием ссылки на список результатов
       :param args: фраза поискового запроса
    """
    if not args[0] : return
    search_term = ''.join(args[0])
    url = 'https://www.youtube.com/results?search_query='+ search_term
    #Настроили браузер
    webbrowser.register('Chrome', None,webbrowser.BackgroundBrowser('C:\\Program Files\Google\Chrome\Application\chrome.exe'))
    webbrowser.get('Chrome').open_new_tab(url)



# Упрощенный словарь команд
commands = {
    ("видео",'ютуб',):search_video_yuotube
}

if __name__ == "__main__":

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()

    # настройка данных голосового помощника
    assistant = VoiceAssistant()
    assistant.name = 'Alice'
    assistant.sex = 'female'
    assistant.speech_language = 'ru'

    # установка голоса по умолчанию
    setup_assistant_voice()

    while True:
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(voice_input)

        # отделение комманд от дополнительной информации (аргументов)
        voice_input = voice_input.split(" ")
        command = voice_input[0]
        command_options = [str(item) for item in voice_input[1:len(voice_input)]]
        execute_command_with_name(command, command_options)

