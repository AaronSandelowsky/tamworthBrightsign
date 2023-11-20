import asyncio
import base64
import json
import tkinter as tk
import numpy as np
import pyaudio
import speech_recognition as sr
import websockets
from configure import auth_key

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)

URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

target_ip = "192.168.5.146"
target_port = 5000
empty_string_count = 0
stop_event = asyncio.Event()


async def send_receive(window, text3):
    print(f'Connecting websocket to URL {URL}')
    NumberOfIssues = 0
    previous_text = ""
    savedText = ""
    evenorodd = 0
    async with websockets.connect(
        URL,
        extra_headers=(("Authorization", auth_key),),
        ping_interval=5,
        ping_timeout=20
    ) as _ws:
        await asyncio.sleep(0.1)
        print("Receiving SessionBegins ...")
        session_begins = await _ws.recv()
        print(session_begins)
        print("Sending messages ...")

        async def send():
            while not stop_event.is_set():
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data": str(data)})

                    await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)

            return True

        async def receive(previous_text, savedText, NumberOfIssues, evenorodd):
            while not stop_event.is_set():
                try:
                    if evenorodd == 0:
                        evenorodd = 0
                    else:
                        evenorodd = 0
                    result_str = await _ws.recv()
                    text_received = json.loads(result_str)['text']
                    textType = json.loads(result_str)['message_type']
                    confidence = json.loads(result_str)['confidence']
                    print(confidence)
                    print(textType)
                    if textType == 'FinalTranscript' and NumberOfIssues == 0:
                        if text_received != savedText:
                            savedText += ' '
                            savedText += text_received + ' '
                    elif len(text_received) < len(previous_text) - 0.75 * len(previous_text):
                        savedText += ' ' + previous_text + ' '
                        NumberOfIssues += 1

                    if previous_text == text_received:
                        NumberOfIssues += 1
                        print(NumberOfIssues)
                    else:
                        NumberOfIssues = 0

                    print("TextSaved:    ", savedText)
                    print("Previous text:", previous_text)
                    print("text_received:", text_received)
                    text_to_display = savedText + text_received

                    if evenorodd == 0:
                        text3.config(text=text_to_display,   
                        foreground="yellow",  # Set the text color to white
                        background="#1A0F62",
                        width=400,
                        height=200,
                        wraplength=1000,
                        font=("Arial", 30)) # Set the background color to black)
                        window.update()

                    if NumberOfIssues > 25:
                        print("Done")
                        # Assuming you have this function defined somewhere
                        # send_text_over_udp("text1:                    Welcome To Tamworth")
                        # send_text_over_udp("text2:EndMessage")
                        NumberOfIssues = 0
                        print(NumberOfIssues)

                        stop_event.set()  # Set the event to stop the coroutine

                        return NumberOfIssues

                    previous_text = text_received

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"

        await asyncio.gather(send(), receive(previous_text, savedText, NumberOfIssues, evenorodd))

        await asyncio.sleep(5)


def main():
    window = tk.Tk()
    window.title("Speech to Text Output")  
    window.geometry("1920x1080") 
    text3 = tk.Label(text="Welcome to Tamworth Airport")
    text3.pack()

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    recognizer.dynamic_energy_threshold = False
    j = 1
    threshold = 0

    while True:
        print("Listening for speech...")
        with microphone as source:
            try:
                audio = recognizer.listen(source, timeout=None)

                audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_data**2))

                if rms > threshold:
                    loop = asyncio.get_event_loop()
                    send_receive_task = loop.create_task(send_receive(window, text3))

                    try:
                        loop.run_until_complete(send_receive_task)
                        return 0
                    except asyncio.CancelledError:
                        print("Task was canceled.")

                    # Assuming you have this function defined somewhere
                    # send_text_over_udp("text2:EndMessage")
            except sr.WaitTimeoutError:
                pass  # No speech detected within the timeout


if __name__ == "__main__":
    main()
