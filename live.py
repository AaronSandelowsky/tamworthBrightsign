import speech_recognition as sr
import socket
import time
from translate import Translator

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

def live_speech_to_text(textToSend,ifMessageStarted, timeout):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    recognizer.dynamic_energy_threshold = False
    print("Listening for speech...")

    with microphone as source:
        while True:
            try:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout =0.5)
                # time1 = time.time()
                recognized_text = recognizer.recognize_google(audio)
                recognized_text = recognized_text.title()
                if len(recognized_text) > 10:
                    timeout = 0 
                textToSend = textToSend + " " + recognized_text + '.'
                print(textToSend)
                if ifMessageStarted == 0 and len(textToSend) > 10:
                    send_text_over_udp("text2:StartMessage")
                    ifMessageStarted = 1
                send_text_over_udp(textToSend)
                # print("Time taken = ", time.time() - time1)
                # translator= Translator(to_lang="zh")
                # translation = translator.translate(textToSend)
                # print(translation)
            except sr.WaitTimeoutError:
                print("timeout")
                timeout = timeout + 1
                if timeout > 5 and ifMessageStarted == 1:
                    delay = 5
                    time.sleep(delay)
                    send_text_over_udp("text2:EndMessage")
                    delay2 = 5
                    time.sleep(delay2)
                    # send_text_over_udp("text3:"+textToSend)
                    send_text_over_udp("text2:StartMessage")
                    send_text_over_udp("text1:              Welcome to Tamworth Airport                 ")
                    send_text_over_udp("text2:EndMessage")
                    timeout = 0
                    ifMessageStarted = 0
                    textToSend = "text1:"
                    break
                pass
            except sr.UnknownValueError:
                print("Could not understand audio")
            except KeyboardInterrupt:
                print("Program stopped.")
                break

if __name__ == "__main__":
    i = 8
    textToSend = "text1:"
    ifMessageStarted = 0
    timeout = 0
    while i > 0:
        live_speech_to_text(textToSend, ifMessageStarted, timeout)