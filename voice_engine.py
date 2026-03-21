import pyttsx3
import threading
import queue
import time

speech_queue = queue.Queue()

def _worker():
    while True:
        # Now expecting: (text, state, is_male)
        data = speech_queue.get()
        if data is None: break
        
        text, state, is_male = data
        
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            target_voice_id = None

            if is_male:
                # Hunt for Mark first, then David
                for v in voices:
                    if "mark" in v.name.lower():
                        target_voice_id = v.id
                        break
                if not target_voice_id:
                    for v in voices:
                        if "david" in v.name.lower():
                            target_voice_id = v.id
                            break
            else:
                # Hunt for Zira specifically for the Female setting
                for v in voices:
                    if "zira" in v.name.lower():
                        target_voice_id = v.id
                        break
            
            # Final fallback
            if not target_voice_id:
                target_voice_id = voices[0].id

            engine.setProperty('voice', target_voice_id)
            engine.setProperty('rate', 185) 
            
            # MOUTH START
            state["is_talking"] = True
            
            engine.say(text)
            engine.runAndWait()
            
            # MOUTH STOP
            state["is_talking"] = False
            
            engine.stop()
            del engine
        except Exception as e:
            print(f"Voice Error: {e}")
            if state: state["is_talking"] = False
        finally:
            speech_queue.task_done()

threading.Thread(target=_worker, daemon=True).start()

def speak(text, state, is_male):
    # Pass the gender preference to the worker
    speech_queue.put((text, state, is_male))