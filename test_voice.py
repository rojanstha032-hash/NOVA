import asyncio
import edge_tts
import subprocess
import os

async def speak(text, voice):
    print(f"\n🔊 Testing: {voice}")
    tts = edge_tts.Communicate(text, voice)
    await tts.save("test_voice.mp3")
    
    # Play the audio
    subprocess.run([
        'powershell', '-c',
        f'Add-Type -AssemblyName presentationCore; '
        f'$player = New-Object system.windows.media.mediaplayer; '
        f'$player.open([uri]"{os.path.abspath("test_voice.mp3")}"); '
        f'$player.play(); '
        f'Start-Sleep 6'
    ])

async def test():
    text = "Hello! I am Nova, your personal AI assistant. How can I help you today Rojan?"
    
    # Only voices that work reliably
    voices = [
        "en-US-JennyNeural",
        "en-US-AriaNeural",
        "en-GB-SoniaNeural",
        "en-AU-NatashaNeural",
    ]
    
    for voice in voices:
        try:
            await speak(text, voice)
            choice = input(f"Did you like {voice}? (y/n): ")
            if choice.lower() == 'y':
                print(f"\n✅ Great choice! Using: {voice}")
                print(f"Add this to config.py: NOVA_VOICE = '{voice}'")
                break
        except Exception as e:
            print(f"❌ {voice} failed: {e}")
            continue

asyncio.run(test())