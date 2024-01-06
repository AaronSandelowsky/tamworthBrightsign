import websockets
import asyncio
import base64
import json
import pyaudio
import speech_recognition as sr
import socket
import time
from translate import Translator
import numpy as np

auth_key = "b9e4ad0231e14b2ba12eb5276fddcea7"
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

def trim_string(input_string, max_length=600, words_to_remove=10):
    words = input_string.split()

    while len(' '.join(words)) > max_length:
        if words_to_remove > 0 and words:
            words = words[words_to_remove:]
        else:
            break

    return ' '.join(words)

def send_text_over_udp(text):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = text.encode('utf-8')
        udp_socket.sendto(data, (target_ip, target_port))
        # print(f"Text sent successfully to {target_ip}:{target_port}")
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

        async def receive(previous_text, savedText,  NumberOfIssues, evenorodd):
            while not stop_event.is_set():  # Continue receiving until the event is set
                try:
                    if(evenorodd == 0):
                        evenorodd = 0
                    else:
                        evenorodd = 0
                    result_str = await _ws.recv()
                    text_received = json.loads(result_str)['text']
                    textType = json.loads(result_str)['message_type']
                    confidence = json.loads(result_str)['confidence']
                    # Add word library
                    print(confidence)
                    print(textType)
                    if(textType == 'FinalTranscript' and NumberOfIssues == 0):
                        if(text_received  != savedText):
                            savedText += ' '
                            savedText += text_received + ' '
                    elif (len(text_received)  < len(previous_text) - 0.75* len(previous_text) ):
                        savedText += ' ' + previous_text +' '
                        NumberOfIssues += 1
                    #Add holding text feature
                    # if (len(text_received)  < len(previous_text) - 10):
                    #     savedText += previous_text
                    
                    if (previous_text == text_received):
                        NumberOfIssues += 1
                        print(NumberOfIssues)
                    else:
                        NumberOfIssues = 0

                    
                    print("TextSaved:    ", savedText)
                    print("Previous text:", previous_text)
                    print("text_received:", text_received)
                    # print("text1:" + savedText + text_received)
                    text_to_display =savedText + text_received
                    text_to_display  = trim_string(text_to_display)
                    if(evenorodd == 0):
                        send_text_over_udp("text1:" + text_to_display)
                    if (NumberOfIssues > 25):
                        print("Done")
                        send_text_over_udp("text1:                    Welcome To Tamworth")
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
        await asyncio.gather(send(), receive(previous_text, savedText, NumberOfIssues, evenorodd))

        await asyncio.sleep(5)


def main():
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

                # Convert audio data to a numpy array for RMS calculation
                audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
        
                # Calculate the RMS value of the audio data
                rms = np.sqrt(np.mean(audio_data**2))
                
                if(rms > threshold):
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