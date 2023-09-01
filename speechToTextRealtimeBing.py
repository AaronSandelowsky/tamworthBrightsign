import speech_recognition as sr
import socket
import time
# Create a recognizer instance
recognizer = sr.Recognizer()

def send_text_over_udp(text, target_ip, target_port):
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Encode the text to bytes
        data = text.encode('utf-8')

        # Send the data over UDP
        udp_socket.sendto(data, (target_ip, target_port))
        print(f"Text sent successfully to {target_ip}:{target_port}")
    except socket.error as e:
        print(f"Error occurred while sending data: {e}")
    finally:
        # Close the socket
        udp_socket.close()
        
        
# Define a function to listen to the microphone and detect speech
def listen_microphone():
    with sr.Microphone() as source:
        print("Listening for announcement...")

        # Adjust ambient noise for better recognition
        recognizer.adjust_for_ambient_noise(source)

       

    
        while True:
            try:
                # Use the Google Speech Recognition service to transcribe audio
                # Listen for speech
                audio = recognizer.listen(source)
                print("annonuncement being made")
                # convert speech to text
                text = recognizer.recognize_wit(audio)
                print("You said:", text)
                print("and", text)
                target_ip = "192.168.5.146"  # Replace this with the target IP address
                target_port = 5000  # Replace this with the target port number
                text_to_send = "Hello, this is a message sent over UDP!"
                send_text_over_udp("text2:StartMessage", target_ip, target_port)
                send_text_over_udp(text, target_ip, target_port)
                delay = 5
                time.sleep(delay)
                send_text_over_udp("text2:EndMessage", target_ip, target_port)
                
            except sr.UnknownValueError:
                print("Could not understand audio")
                break
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except KeyboardInterrupt:
                print("Stopping microphone sensing...")
                break

        

# Call the listen_microphone function to start listening
i = 1
while(i > 0):
    listen_microphone()
