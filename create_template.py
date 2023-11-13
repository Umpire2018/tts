import os
import time
from azure.cognitiveservices.speech import SpeechSynthesizer, AudioConfig, ResultReason, CancellationReason
from config import speech_config

# Default list of voice names
default_voice_names = [
    "XiaoxiaoNeural（女）", "YunxiNeural（男）", "YunjianNeural（男）", "XiaoyiNeural（女）",
    "YunyangNeural（男）", "XiaochenNeural（女）", "XiaohanNeural（女）", "XiaomengNeural（女）",
    "XiaomoNeural（女）", "XiaoqiNeural（女）", "XiaoruNeural（女）", "XiaoshuangNeural（女性，儿童）",
    "XiaoxuanNeural（女）", "XiaoyanNeural（女）", "XiaoyouNeural（女性，儿童）", "XiaozhenNeural（女）",
    "YunfengNeural（男）", "YunhaoNeural（男）", "YunxiaNeural（男）", "YunyeNeural（男）",
    "YunzeNeural（男）", "XiaorouNeural1（女）", "YunjieNeural1（男）"
]

# Check if voice_names.txt exists, if not, create it with the default list
voice_names_file = 'voice_names.txt'
if not os.path.exists(voice_names_file):
    with open(voice_names_file, 'w', encoding='utf-8') as file:
        for name in default_voice_names:
            file.write(f"{name}\n")

# Read voice names from the file
with open(voice_names_file, 'r', encoding='utf-8') as file:
    voice_names = [line.strip() for line in file if line.strip()]

# Path to the folder where you want to save the audio files.
output_folder = "template"

# Check if the output folder exists, if not, create it.
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Number of retries for network interactions
max_retries = 3
retry_delay = 5  # seconds

# Example text to be synthesized.
example_text = "这是一个示例文本，用于演示文本到语音的转换。"

# Function to synthesize speech with retries
def synthesize_voice(voice_name_details, speech_config, output_folder, max_retries, retry_delay):
    # Extract voice name and gender from the details
    voice_name, gender = voice_name_details.rsplit('（', 1)
    gender = gender.rstrip('）')
    gender = gender.replace('女性', '女').replace('儿童', '童')  # Simplify gender notation

    # Set the voice name in the speech config.
    speech_config.speech_synthesis_voice_name = f"zh-CN-{voice_name}"

    for attempt in range(max_retries):
        try:
            # Initialize speech synthesizer.
            synthesizer = SpeechSynthesizer(speech_config=speech_config)

            # Get the path to the output audio file.
            file_path = os.path.join(output_folder, f"{voice_name}_{gender}.wav")

            audio_config = AudioConfig(filename=file_path)

            # Use the synthesizer with the specified audio configuration
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            # Synthesize the voice name to a file.
            result = synthesizer.speak_text_async(example_text).get()

            # Check the result and break the loop if successful.
            if result.reason == ResultReason.SynthesizingAudioCompleted:
                print(f"Speech synthesized for voice {voice_name} and saved to {file_path}")
                return
            elif result.reason == ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.reason == CancellationReason.Error:
                    if cancellation_details.error_details:
                        print(f"Error details: {cancellation_details.error_details}")
                        raise Exception(cancellation_details.error_details)
        except Exception as e:
            print(f"An error occurred: {e}. Retrying in {retry_delay} seconds.")
            time.sleep(retry_delay)
        

    print(f"Failed to synthesize voice {voice_name} after {max_retries} attempts.")

# Loop through each voice name and synthesize speech
for voice_name_details in voice_names:
    synthesize_voice(voice_name_details, speech_config, output_folder, max_retries, retry_delay)
