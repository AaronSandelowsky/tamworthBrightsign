#
#    Copyright 2018-2023 Picovoice Inc.
#
#    You may not use this file except in compliance with the license. A copy of the license is located in the "LICENSE"
#    file accompanying this source.
#
#    Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
#    specific language governing permissions and limitations under the License.
#

import argparse
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

from pvcheetah import CheetahActivationLimitError, create
from pvrecorder import PvRecorder
\
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
        # print(f"Text sent successfully to {target_ip}:{target_port}")
    except socket.error as e:
        print(f"Error occurred while sending data: {e}")
    finally:
        udp_socket.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--access_key',
        default = 'OKA5wYBWQRt1p/cGcJNwMAFeU0lv4t4klyumlQTR4G/Izk6cnFM7FA==')
    parser.add_argument(
        '--library_path',
        help='Absolute path to dynamic library. Default: using the library provided by `pvcheetah`')
    parser.add_argument(
        '--model_path',
        help='Absolute path to Cheetah model. Default: using the model provided by `pvcheetah`')
    parser.add_argument(
        '--endpoint_duration_sec',
        type=float,
        default=1.,
        help='Duration in seconds for speechless audio to be considered an endpoint')
    parser.add_argument(
        '--disable_automatic_punctuation',
        action='store_true',
        help='Disable insertion of automatic punctuation')
    parser.add_argument('--audio_device_index', type=int, default=-1, help='Index of input audio device')
    parser.add_argument('--show_audio_devices', action='store_true', help='Only list available devices and exit')
    args = parser.parse_args()

    if args.show_audio_devices:
        for index, name in enumerate(PvRecorder.get_available_devices()):
            print('Device #%d: %s' % (index, name))
        return

    if not args.access_key:
        print('--access_key is required.')
        return

    cheetah = create(
        access_key=args.access_key,
        library_path=args.library_path,
        model_path=args.model_path,
        endpoint_duration_sec=args.endpoint_duration_sec,
        enable_automatic_punctuation=not args.disable_automatic_punctuation)

    try:
        print('Cheetah version : %s' % cheetah.version)

        recorder = PvRecorder(frame_length=cheetah.frame_length, device_index=args.audio_device_index)
        recorder.start()
        print('Listening... (press Ctrl+C to stop)')
        message1 = ""
        try:
            while True:
                partial_transcript, is_endpoint = cheetah.process(recorder.read())
                message1 = message1 + partial_transcript
                print(partial_transcript)
                send_text_over_udp(message1)
                
                if is_endpoint:
                    print(cheetah.flush())
                    message1 = message1 + cheetah.flush()
                    # print(message1)
        finally:
            print()
            print("recorder stopped")
            recorder.stop()

    except KeyboardInterrupt:
        pass
    except CheetahActivationLimitError:
        print('AccessKey has reached its processing limit.')
    finally:
        cheetah.delete()


if __name__ == '__main__':
    main()