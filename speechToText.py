import speech_recognition as sr
import socket
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

        # Listen for speech
        audio = recognizer.listen(source)

        print("Announcement being made")

        try:
            # Use the Google Speech Recognition service to transcribe audio
            
            print("start message")
            audio_data = recognizer.record(source, duration=5)
            print("end message")
            print("Loading...")
            # convert speech to text
            text = recognizer.recognize_google(audio_data)
            print(text)
            text = "text1:" + text
            print("and", text)
            target_ip = "192.168.5.146"  # Replace this with the target IP address
            target_port = 5000  # Replace this with the target port number
            text_to_send = "Hello, this is a message sent over UDP!"
            send_text_over_udp(text, target_ip, target_port)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")


# Call the listen_microphone function to start listening
i = 1
while(i > 0):
    listen_microphone()
