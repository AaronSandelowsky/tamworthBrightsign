import websockets
import asyncio
import base64
import json
from configure import auth_key
import pyaudio
import speech_recognition as sr
import socket
import time
from translate import Translator


FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

# starts recording
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)

# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

# Define target IP and port
target_ip = "192.168.5.146"
target_port = 5000
empty_string_count = 0
# Function to send text over UDP


def send_text_over_udp(text):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = text.encode('utf-8')
        udp_socket.sendto(data, (target_ip, target_port))
        print(f"Text sent successfully to {target_ip}:{target_port}")
    except socket.error as e:
        print(f"Error occurred while sending data: {e}")
    finally:
        udp_socket.close()


# Define a global event to signal when to stop the coroutine
stop_event = asyncio.Event()


async def send_receive():
    print(f'Connecting websocket to URL {URL}')
    NumberOfIssues = 0
    previous_text = ""
    savedText = ""
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
            while not stop_event.is_set():  # Continue sending until the event is set
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

        async def receive(previous_text, savedText,  NumberOfIssues):
            while not stop_event.is_set():  # Continue receiving until the event is set
                try:
                    result_str = await _ws.recv()
                    text_received = json.loads(result_str)['text']
                    textType = json.loads(result_str)['message_type']
                    confidence = json.loads(result_str)['confidence']
                    print(confidence)
                    print(textType)
                    if(textType == 'FinalTranscript' and NumberOfIssues == 0):
                        savedText += text_received
                    
                    
                    if (previous_text == text_received):
                        NumberOfIssues += 1
                        print(NumberOfIssues)
                    else:
                        NumberOfIssues = 0

                    if (len(text_received)  == 0):
                        savedText += previous_text
                    print("text1:" + savedText + text_received)
                    send_text_over_udp("text1:" + savedText + text_received)
                    if (NumberOfIssues > 10):
                        print("Done")
                        send_text_over_udp("text1:                  Welcome To Tamworth")
                        send_text_over_udp("text2:EndMessage")
                        NumberOfIssues = 0
                        print(NumberOfIssues)

                        # Set the event to stop the coroutine
                        stop_event.set()

                        return NumberOfIssues

                    previous_text = text_received

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"

        # Start sending and receiving asynchronously
        await asyncio.gather(send(), receive(previous_text, savedText, NumberOfIssues))

        await asyncio.sleep(5)


def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    recognizer.dynamic_energy_threshold = False
    j = 1

    while True:
        print("Listening for speech...")
        with microphone as source:
            try:
                audio = recognizer.listen(source, timeout=None)
                text = recognizer.recognize_google(audio)
                print("Speech detected:", text)
                send_text_over_udp("text2:StartMessage")

                # Create and run the asyncio event loop
                loop = asyncio.get_event_loop()
                send_receive_task = loop.create_task(send_receive())

                try:
                    # Wait for the coroutine to complete
                    loop.run_until_complete(send_receive_task)
                    return 0
                except asyncio.CancelledError:
                    # Handle task cancellation
                    print("Task was canceled.")

                send_text_over_udp("text2:EndMessage")
            except sr.WaitTimeoutError:
                pass  # No speech detected within the timeout


if __name__ == "__main__":
    main()
