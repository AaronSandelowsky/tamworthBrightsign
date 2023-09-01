import speech_recognition as sr
import socket
import time

# Create a recognizer instance
recognizer = sr.Recognizer()

# Define target IP and port
target_ip = "192.168.5.146"
target_port = 5000

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

# Function to listen to the microphone and detect speech
def listen_microphone():
    with sr.Microphone() as source:
        print("Listening for announcement...")
        recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                audio = recognizer.listen(source)
                print("Announcement being made")

                text = recognizer.recognize_google(audio, language="en-AU")
                print("You said:", text)

                text = "text1:" + text
                send_text_over_udp("text2:StartMessage")
                send_text_over_udp(text)
                delay = 5
                time.sleep(delay)
                send_text_over_udp("text2:EndMessage")
                last_message_time = time.time()
                delay2 = 5
                time.sleep(delay2)
                send_text_over_udp("text2:HideMessage")

            except sr.UnknownValueError:
                print("Could not understand audio")
                send_text_over_udp("text2:HideMessage")
                break
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except KeyboardInterrupt:
                print("Stopping microphone sensing...")
                break

# Start of the main program
#Scrolling
i = 1
while i > 0:
    listen_microphone()
