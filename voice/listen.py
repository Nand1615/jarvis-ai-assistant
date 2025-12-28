import speech_recognition as sr


def listen():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        return text.lower()

    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None
    except Exception:
        return None
