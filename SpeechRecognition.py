import speech_recognition as sr
import socketio
import datetime
import uuid


for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))


def send_detected_voice(text, time, uniqueId):
    detestedVoice = {}
    detestedVoice["comment"] = text
    detestedVoice["time"] = time
    detestedVoice["uniqueId"] = uniqueId
    return detestedVoice


def speech_recognition():
    sio = socketio.Client()
    sio.connect('https://univas.herokuapp.com/')
    
    print("なにか話してください")

    while True:

        # 音声入力
        r = sr.Recognizer()

        #print(sr.Microphone.list_microphone_names())
        #device_index=0
        with sr.Microphone(device_index=3) as source:

            audio = r.listen(source)

        try:
            # Google Web Speech APIで音声認識 ko-KR  en-US ja-JP
            text = r.recognize_google(audio, language="ja-JP")

        except sr.UnknownValueError:
            text = None
            print("音声を認識できませんでした")

        except sr.RequestError as e:
            text = None
            print("音声認識を要求できませんでした: {0}".format(e))

        else:
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            formated_time = str(time)
            uniqueId = 'FRIST'
            sio.emit('send-detected-voice', send_detected_voice(text, formated_time, uniqueId))

        finally:
            print(text)
            text = None


if __name__ == '__main__':
    speech_recognition()
