#!/usr/bin/env python3
from swiftwhisper import StreamHandler
from bs4 import BeautifulSoup
from subprocess import call
import wikipedia, requests
import pyttsx3, media_control
import time, os, re

AIname = "computer"
City = ''

Model = 'small'
English = False
Translate = False
SampleRate = 44100
BlockSize = 30
Threshold = 0.1
Vocals = [50, 1000]
EndBlocks = 40

class Assistant:
    def __init__(self):
        self.running = True
        self.talking = False
        self.prompted = False
        self.espeak = pyttsx3.init()
        self.espeak.setProperty('rate', 180)
        self.askwiki = False
        self.weatherSave = ['',0]
        self.ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'
        self.wake_required = os.environ.get('WAKE_WORD_REQUIRED', '0') not in ('0','false','no','off','')

    def analyze(self, input):
        string = "".join(ch for ch in input if ch not in ",.?!'").lower()
        query = string.split()
        if query in ([AIname],["hey",AIname],["okay",AIname],["ok",AIname]):
            self.speak('Yes?')
            self.prompted = True
        # Wake word optional
        queried = False
        try:
            if self.prompted or (not self.wake_required):
                queried = True
            elif string.startswith((AIname,"hey "+AIname,"okay "+AIname,"ok "+AIname)):
                queried = True
        except Exception:
            queried = True
        if queried:
            query = [word for word in query if word not in {"hey","okay","ok",AIname}]
        ru = 'ё' in string or any('а'<=ch<='я' for ch in string)
        if self.askwiki or (queried and ("wikipedia" in query or "wiki" in query or (ru and ("википедия" in query or "вики" in query)))):
            wikiwords = {"okay","hey",AIname,"please","could","would","do","a","check","i","need","wikipedia",
                        "search","for","on","what","whats","who","whos","is","was","an","does","say","can",
                        "you","tell","give","get","me","results","info","information","about","something","ok",
                        "википедия","вики","скажи","покажи","расскажи","найди","что","кто","про","о"}
            query = [word for word in query if word not in wikiwords]
            if query == [] and not self.askwiki:
                self.speak("What would you like to know about?")
                self.askwiki = True
            elif query == [] and self.askwiki:
                self.speak("No search term given, canceling.")
                self.askwiki = False
            else:
                self.speak(self.getwiki(" ".join(query)))
                self.askwiki = False
            self.prompted = False
        elif queried and (re.search(r"(song|title|track|name|playing)+", ' '.join(query)) or (ru and re.search(r"(трек|песня|название)+", ' '.join(query)))):
            self.speak(media_control.status()[0]['title'])
            self.prompted = False
        elif queried and (re.search(r"(play|pause|unpause|resume)+", ' '.join(query)) or (ru and re.search(r"(играй|проигрывай|пауза|продолжи)+", ' '.join(query)))):
            media_control.playpause()
            self.prompted = False
        elif queried and ("stop" in query or (ru and ("стоп" in query or "останови" in query))):
            media_control.stop()
            self.prompted = False
        elif queried and ("next" in query or "forward" in query or "skip" in query or (ru and ("следующий" in query or "вперед" in query or "дальше" in query))):
            media_control.next()
            self.prompted = False
        elif queried and ("previous" in query or "back" in query or "last" in query or (ru and ("предыдущий" in query or "назад" in query or "прошлый" in query))):
            media_control.prev()
            self.prompted = False
        elif queried and (re.search(r"^(volume (up|louder)|(louder|more) (music|volume)|turn (it|the (music|volume|sound)) up( more)?|turn up the (music|volume|sound)|(increase|raise) the (volume|sound))( more)?$", ' '.join(query)) or (ru and ("громче" in query or "увеличь" in query))):
            media_control.volumeup()
            self.prompted = False
        elif queried and (re.search(r"^(volume (down|lower)|(lower|less) (music|volume)|turn (it|the (music|volume|sound)) down( more)?|turn down the (music|volume|sound)|(decrease|lower) the (volume|sound))( more)?$", ' '.join(query)) or (ru and ("тише" in query or "уменьши" in query))):
            media_control.volumedown()
            self.prompted = False
        elif queried and ("weather" in query or (ru and "погода" in query)):
            self.speak(self.getweather())
            self.prompted = False
        elif queried and ("time" in query or (ru and "время" in query)):
            self.speak(time.strftime("The time is %-I:%M %p."))
            self.prompted = False
        elif queried and ("date" in query or (ru and "дата" in query)):
            self.speak(time.strftime(f"Today's date is %B {self.orday()} %Y."))
            self.prompted = False
        elif queried and ("day" in query or "today" in query or (ru and ("день" in query or "сегодня" in query))):
            self.speak(time.strftime(f"It's %A the {self.orday()}."))
            self.prompted = False
        elif queried and ("joke" in query or "jokes" in query or "funny" in query or (ru and ("шутка" in query or "анекдот" in query))):
            try:
                joke = requests.get('https://icanhazdadjoke.com', headers={'Accept':'text/plain','User-Agent':self.ua}).text
            except requests.exceptions.ConnectionError:
                joke = "I can't think of any jokes right now. Connection Error."
            self.speak(joke)
            self.prompted = False
        elif queried and ("terminate" in query or (ru and ("заверши" in query or "выход" in query or "закрой" in query))):
            self.running = False
            self.speak("Closing Assistant.")
        elif queried and len(query) > 2:
            self.speak(self.getother('+'.join(query)))
            self.prompted = False

    def speak(self, text):
        if self.talking:
            return
        self.talking = True
        try:
            print(f"\n{text}\n")
            try:
                self.espeak.stop()
            except Exception:
                pass
            self.espeak.say(text)
            self.espeak.runAndWait()
        except Exception:
            try:
                self.espeak = pyttsx3.init()
                self.espeak.setProperty('rate', 180)
                self.espeak.say(text)
                self.espeak.runAndWait()
            except Exception:
                pass
        finally:
            self.talking = False

    def getweather(self) -> str:
        curTime = time.time()
        if curTime - self.weatherSave[1] > 300 or self.weatherSave[1] == 0:
            try:
                html = requests.get("https://www.google.com/search?q=weather"+City, {'User-Agent':self.ua}).content
                soup = BeautifulSoup(html, 'html.parser')
                loc = soup.find("span",attrs={"class":"BNeawe tAd8D AP7Wnd"}).text.split(',')[0]
                skyc = soup.find('div', attrs={'class':'BNeawe tAd8D AP7Wnd'}).text.split('\n')[1]
                temp = soup.find('div', attrs={'class':'BNeawe iBp4i AP7Wnd'}).text
                temp += 'ahrenheit' if temp[-1] == 'F' else 'elcius'
                self.weatherSave[0] = f'Current weather in {loc} is {skyc}, with a temperature of {temp}.'
                self.weatherSave[1] = curTime
            except requests.exceptions.ConnectionError:
                return "I couldn't connect to the weather service."
        return self.weatherSave[0]

    def getwiki(self, text) -> str:
        try:
            wikisum = wikipedia.summary(text, sentences=2, auto_suggest=False)
            wikipage = wikipedia.page(text, auto_suggest=False)
            try:
                call(['notify-send','Wikipedia',wikipage.url])
            finally:
                return 'According to Wikipedia:\n'+wikisum
        except (wikipedia.exceptions.PageError, wikipedia.exceptions.WikipediaException):
            return "I couldn't find that right now, maybe phrase it differently?"

    def getother(self, text) -> str:
        try:
            html = requests.get("https://www.google.com/search?q="+text, {'User-Agent':self.ua}).content
            soup = BeautifulSoup(html, 'html.parser')
            return soup.find('div', attrs={'class':'BNeawe iBp4i AP7Wnd'}).text
        except:
            return "Sorry, I'm afraid I can't do that."

    def orday(self) -> str:
        day = time.strftime("%-d")
        return day+'th' if int(day) in [11,12,13] else day+{1:'st',2:'nd',3:'rd'}.get(int(day)%10,'th')

def main():
    try:
        AIstant = Assistant()
        handler = StreamHandler(AIstant)
        handler.listen()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\nQuitting..")
        if os.path.exists('dictate.wav'):
            os.remove('dictate.wav')

if __name__ == '__main__':
    main()


