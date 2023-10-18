import pyttsx3

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", "voices[2].id")
engine.setProperty("rate", 178)


def speak(text):
    engine.say(text)
    engine.runAndWait()
