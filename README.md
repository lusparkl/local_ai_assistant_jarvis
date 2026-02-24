# Jarvis. Fully local AI assistant.

## Fully functional, but still unfinished AI assistant written on Python thats works on your PC!

This project is my recreation of the J.A.R.V.I.S from "Iron Man" movie. He can listen, think, speak, memorize and most important use ANY tools you provide him. It's very customizable project.

## Short trailer for the project, haven't covered all features, but I really worked hard to create it!

[![Jarvis Trailer](https://img.youtube.com/vi/jkSiXKr-uqs/hqdefault.jpg)](http://www.youtube.com/watch?v=jkSiXKr-uqs "Jarvis Trailer")

## Deps:

* Cuda - not neccesary, but without it it'll be too slow
* Python >3.11 3.13< - because of tts library we can't run on 3.14 at the moment, but I hope soon they'll update it

## Main libraries I used to build Jarvis:

* [ollama](https://github.com/ollama/ollama-python)
* [coqui-ai-TTS](https://github.com/idiap/coqui-ai-TTS)
* [faster whisper](https://github.com/SYSTRAN/faster-whisper)
* [chroma](https://github.com/chroma-core/chroma)
* [sounddevice](https://github.com/spatialaudio/python-sounddevice)
* [openwakeword](https://github.com/dscripka/openWakeWord)

**Many thanks to the devs!!**

## How to install Jarvis to your PC

1. Copy this repo to your pc.
2. Install all requirements with '''pip install -r requirements.txt'''
3. Run '''python -m setup.download_models''' to download needed models and then paste their pathes from console to your config.py.
4. Test run with python main.py, you can already use him this way!
5. Run '''pyinstaller --onefile main.py''' to turn jarvis to .exe file, don't forget to test before doing it!
6. Start up jarvis automaticaly with windows task scheduler, or smth similar if you're on linux/mac. This is good [tutorial](https://thecodebuzz.com/schedule-run-exe-console-application-windows-task-scheduler/).

## How to tweak this project for your own uses

Since I'm trying to write modular project It'll be easy to change modules as you want. You can completly change tts model or even switch to some api(what I'll totaly understand, because it might be really slow on weak PC's). 

But the easisest way - add your tools. You can write tools that YOU really need, and I'm sure that there will be some, because I'm writing only tools that almost everyone needs. Now to add your tool you need:
1. Create your file or write code in existing if theme is the same in the /tools
2. Write your tool function that AI will use, you can use my functions as examples. And don't forget about commenting your function so AI will understand what it's for!!
3. Import and add your tool to the services/manage_tools. You can disable tools by setting value in front of it's name to False btw

Your tool is now working!

## Find a bug?

I'm sure that next few weeks this project will be all in bugs because I haven't even tested it perciselly by myself, only short conversations. So if you found a bug, please submit an issue using the issues tab above. I'll try to fix all issues as fast as possible!

