# coding:utf-8
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import sys
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import threading
import os

client = OpenAI()


# OPENAI_API_KEY='YOUR_API_KEY'


# Metin tabanlı assitan gpt-4-turbo api
def metin(komut):
    if komut.strip().lower() == 'görsel':
        return 'görsel'
    elif komut.strip().lower() == 'kapat':
        print('AI : Kapatılıyor.')
        text_to_speech_and_play('Kapatılıyor.')
        sys.exit()
    else:

        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": komut}]
        )

        return completion.choices[0].message.content


# Metinden görsele dall-e-3 api
def gorsel(komut):
    if komut.strip().lower() == 'asistan':
        return 'asistan'
    elif komut.strip().lower() == 'kapat':
        print('AI : Kapatılıyor.')
        text_to_speech_and_play('Kapatılıyor.')
        sys.exit()
    else:
        text_to_speech_and_play('Görsel oluşturuluyor.')
        response = client.images.generate(
            model="dall-e-3",
            prompt=komut,
            size="1024x1024",
            quality="standard",
            n=1,
        )

    image_url = response.data[0].url
    res = requests.get(image_url)

    if res.status_code == 200:
        img = Image.open(BytesIO(res.content))
        img.show()
    else:
        print("Görüntü alınamadı. Hata kodu:", res.status_code)


# Sesli komutu text dosyasına yazma

def speech_to_text(language="tr-TR"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Sizi dinliyorum.")
        recognizer.adjust_for_ambient_noise(source, duration=0.02)

        audio = None
        try:
            audio = recognizer.listen(source, timeout=15)
        except sr.WaitTimeoutError:
            return "Zaman aşımına uğradı. Lütfen tekrar deneyin."
        except KeyboardInterrupt:
            print("İşlem klavye ile kesildi.")
            sys.exit()

    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "Sizi anlayamadım. Lütfen tekrar söyleyin."
    except sr.RequestError as e:
        return f"Google Speech Recognition hizmetine ulaşılamadı; hata: {e}"


def text_to_speech_and_play(text):
    """Metni sese dönüştürüp çalar ve ardından mp3 dosyasını siler"""
    if text is None:
        print("Geçerli bir metin sağlanmadı.")
        return

    output_file = "response.mp3"
    tts = gTTS(text=text, lang="tr")
    tts.save(output_file)

    def play_sound():
        playsound(output_file)

    sound_thread = threading.Thread(target=play_sound)
    sound_thread.start()
    sound_thread.join()  # Thread tamamlanana kadar bekle

    # Dosya silmeden önce kontrol et
    if os.path.exists(output_file):
        os.remove(output_file)
    else:
        print("Dosya bulunamadı, silme işlemi başarısız.")


def run(komut):
    while (True):
        if (komut == 'asistan'):
            prompt = speech_to_text()
            print('U : ', prompt)
            if (metin(prompt) == 'görsel'):
                print('AI : Ne çizmemi istersiniz ?')
                text_to_speech_and_play('Ne çizmemi istersiniz ?')
                prompt = speech_to_text()
                gorsel(prompt)
            else:
                cevap = metin(prompt)
                print('AI : ', cevap)
                text_to_speech_and_play(cevap)
        elif (komut == 'görsel'):
            prompt = speech_to_text()
            print('U : ', prompt)
            if (gorsel(prompt) != 'asistan'):
                print('AI : Ne çizmemi istersiniz ?')
                text_to_speech_and_play('Ne çizmemi istersiniz ?')
            elif (gorsel(prompt) == 'asistan'):
                print('AI : Size nasıl yardımcı olabilirim ?')
                text_to_speech_and_play('Size nasıl yardımcı olabilirim ?')
                prompt = speech_to_text()
                print('U : ', prompt)
                cevap = metin(prompt)
                text_to_speech_and_play(cevap)
                print('U : ', cevap)


print('*** Ugur Cakir | ugrcakir@outlook.com.tr ***')
print('Asistan | Görsel | Kapat seçeneklerinden birini seçiniz.')
text_to_speech_and_play('Asistan | Görsel | Kapat seçeneklerinden birini seçiniz.')
secim = speech_to_text()

if (secim == 'kapat'):
    print(secim)
    text_to_speech_and_play('Kapatılıyor.')
    sys.exit()
elif (secim == 'asistan'):
    print(secim)
    sonuc = secim
elif (secim == 'görsel'):
    print(secim)
    sonuc = secim
else:
    hata = 'Hatalı komut girdiniz. Tekrar deneyin.'
    print(hata)
    text_to_speech_and_play(hata)

run(secim)
