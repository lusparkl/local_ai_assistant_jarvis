# Jarvis. Fully local AI assistant.

## Fully functional, but still unfinished AI assistant written on Python thats works on your PC!

This project is my recreation of the J.A.R.V.I.S from "Iron Man" movie. He can listen, think, speak, memorize and most important use ANY tools you provide him. Currently I already wrote tools like:

* Weather fetching
* Keyboard interactions(read and copy stuff to your clipboard)
* Create and edit todos

More coming soon!

## Check it out!

Place for vid, I'll update it when create first ship!

## Main libraries I used to build Jarvis:

* [ollama](https://github.com/ollama/ollama-python)
* [coqui-ai-TTS](https://github.com/idiap/coqui-ai-TTS)
* [faster whisper](https://github.com/SYSTRAN/faster-whisper)
* [chroma](https://github.com/chroma-core/chroma)
* [sounddevice](https://github.com/spatialaudio/python-sounddevice)
* [openwakeword](https://github.com/dscripka/openWakeWord)

**Many thanks to the devs!!**

## How to install Jarvis to your PC

Now the only way is to copy this repo and then to play with it for few hours:/

But soon enought I'll start on working on the tutorial and may be even load Jarvis to some platform that will allow you to download him without any head aches.


## How to tweak this project for your own uses

Since I'm trying to write modular project It'll be easy to change modules as you want. You can completly change tts model or even switch to some api(what I'll totaly understand, because it might be really slow on weak PC's). 

But the easisest way - add your tools. You can write tools that YOU really need, and I'm sure that there will be some, because I'm writing only tools that almost everyone needs. Now to add your tool you need:
1. Create your file or write code in existing if theme is the same in the /tools
2. Write your tool function that AI will use, you can use my functions as examples. And don't forget about commenting your function so AI will understand what it's for!!
3. Import and add your tool to the services/manage_tools. You can disable tools by setting value in front of it's name to False btw

Your tool is now working!

## Find a bug?

I'm sure that next few weeks this project will be all in bugs because I haven't even tested it perciselly by myself, only short conversations. So if you found a bug, please submit an issue using the issues tab above. I'll try to fix all issues as fast as possible!

