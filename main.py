import re
from azure.cognitiveservices.speech import SpeechSynthesizer, AudioConfig, ResultReason, CancellationReason
import os
from config import speech_config
from datetime import datetime

def srt_time_to_milliseconds(srt_time):
    time_format = '%H:%M:%S,%f'
    delta = datetime.strptime(srt_time, time_format) - datetime.strptime('00:00:00,000', time_format)
    return int(delta.total_seconds() * 1000)  # Return milliseconds

def wrap_english_words(text):
    # Regex to identify English words
    english_words_pattern = re.compile(r'\b[A-Za-z-]+\b')
    def replace_with_lang_tag(match):
        word = match.group(0)
        # Return the word wrapped in a lang tag
        return f'<lang xml:lang="en-US">{word}</lang>'
    # Replace all English words with lang tags
    return english_words_pattern.sub(replace_with_lang_tag, text)

# Convert SRT to SSML with breaks, durations, and voice tags
def convert_srt_to_ssml(srt_text, voice_name="zh-CN-XiaoxiaoNeural"):
    ssml_parts = [
        f'<speak version="1.0" '
        f'xmlns="http://www.w3.org/2001/10/synthesis" '
        f'xmlns:mstts="http://www.w3.org/2001/mstts" '
        f'xml:lang="zh-CN">'
    ]
    prev_end_time_ms = 0

    # Regex pattern for SRT blocks
    pattern = re.compile(r'^\d+\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.*)$', re.MULTILINE)

    # Parse SRT text and generate SSML
    for match in re.finditer(pattern, srt_text):
        start_time, end_time, text = match.groups()

        # Calculate durations and breaks
        start_time_ms = srt_time_to_milliseconds(start_time)
        end_time_ms = srt_time_to_milliseconds(end_time)
        duration_ms = end_time_ms - start_time_ms
        if prev_end_time_ms > 0:
            break_ms = start_time_ms - prev_end_time_ms
            # Now the break is inside the voice tag
            break_tag = f'<break time="{break_ms}ms"/>'
        else:
            break_tag = ""

        # Wrap English words with lang tag for English pronunciation
        wrapped_text = wrap_english_words(text)

        # Append text with specified duration and voice tag
        ssml_parts.append(
            f'<voice name="{voice_name}">'
            f'{break_tag}'
            f'<mstts:express-as type="general" mstts:audioduration="{duration_ms}">'
            f'{wrapped_text}</mstts:express-as>'
            f'</voice>'
        )

        prev_end_time_ms = end_time_ms

    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

def synthesize_ssml_to_audio(ssml_text, output_folder, file_name):
    # Make sure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    speech_config.speech_synthesis_language = "zh-CN"  # Set the language to Chinese

    # Create audio configuration pointing to our output file
    file_path = os.path.join(output_folder, f"{file_name}.wav")
    audio_output = AudioConfig(filename=file_path)

    # Initialize synthesizer
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)

    # Perform the synthesis
    result = synthesizer.speak_ssml_async(ssml_text).get()

    # Check the result
    if result.reason == ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized to [{file_path}]")
    elif result.reason == ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

# Example usage
srt_text = """
1
00:00:00,000 --> 00:00:04,300
大家好,我们现在来进行 X-Agent 项目的环境搭建

2
00:00:06,300 --> 00:00:10,400
第一步首先是安装项目所需要用到的 Docker Compose
"""

# Convert to SSML
ssml_output = convert_srt_to_ssml(srt_text)
print(ssml_output)

# Synthesize the SSML to audio and save to 'Output' folder
#synthesize_ssml_to_audio(ssml_output, "Output", "synthesized_audio")