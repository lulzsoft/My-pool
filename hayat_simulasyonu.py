# -*- coding: utf-8 -*-

import random
import os
import time

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Oyuncu:
    def __init__(self, isim):
        self.isim = isim
        self.yas = 18
        self.para = 1000
        self.saglik = 100
        self.mutluluk = 100
        self.enerji = 100
        self.zeka = 50
        self.sosyal_beceri = 50
        self.aclik = 0
        self.hijyen = 100
        self.envanter = []
        self.is_emegi = 0 # Kariyer ilerlemesi için

magaza_esyalari = {
    "kitap": {"fiyat": 75, "etki": "zeka", "deger": 5},
    "konsol oyunu": {"fiyat": 200, "etki": "mutluluk", "deger": 15},
    "yemek": {"fiyat": 20, "etki": "aclik", "deger": -30},
    "sabun": {"fiyat": 10, "etki": "hijyen", "deger": 20}
}

def main():
    """Ana oyun fonksiyonu."""
    clear_screen()
    isim = input("Karakterinizin ismini girin: ")
    oyuncu = Oyuncu(isim)

    print(f"\n{oyuncu.isim} adında yeni bir hayata başlıyorsun!")
    time.sleep(2)

    print("\nBaşlangıç Değerlerin:")
    print(f"Yaş: {oyuncu.yas}")
    print(f"Para: {oyuncu.para} TL")
    print(f"Sağlık: {oyuncu.saglik}")
    print(f"Mutluluk: {oyuncu.mutluluk}")
    time.sleep(4)

    oyun_bitti = False
    gun = 1
    while not oyun_bitti:
        durumu_goster(oyuncu, gun)
        eylem_sec(oyuncu)
        gunu_ilerlet(oyuncu, gun)
        gun += 1

        if oyuncu.saglik <= 0:
            oyun_bitti = True
            print("\nSağlığın tükendi ve hayatını kaybettin. Oyun bitti.")

def gunu_ilerlet(oyuncu, gun):
    """Zamanı bir gün ilerletir ve statları günceller."""
    if gun % 365 == 0:
        oyuncu.yas += 1
        print(f"\nDoğum günün kutlu olsun! Artık {oyuncu.yas} yaşındasın.")
        time.sleep(2)

    oyuncu.aclik = min(100, oyuncu.aclik + 10)
    oyuncu.hijyen = max(0, oyuncu.hijyen - 5)

    if oyuncu.aclik >= 80:
        oyuncu.saglik -= 5
        print("\nÇok açsın! Sağlığın azalıyor.")
        time.sleep(1)

    if oyuncu.hijyen <= 20:
        oyuncu.mutluluk -= 5
        print("\n kendini kirli hissediyorsun, bu durum moralini bozuyor.")
        time.sleep(1)

    rastgele_olay(oyuncu)

def rastgele_olay(oyuncu):
    """Her günün sonunda rastgele bir olay tetikler."""
    olasilik = random.randint(1, 100)
    if olasilik <= 5: # %5 ihtimal
        print("\nSürpriz! Yolda 100 TL buldun!")
        oyuncu.para += 100
        oyuncu.mutluluk += 10
        time.sleep(2)
    elif olasilik <= 10: # %5 ihtimal
        print("\nKötü haber... Aniden hastalandın ve doktora gitmek zorunda kaldın.")
        oyuncu.saglik -= 20
        oyuncu.para -= 50
        oyuncu.mutluluk -= 15
        time.sleep(2)
    elif olasilik <= 15: # %5 ihtimal
        print("\nBir arkadaşınla karşılaştın ve keyifli bir sohbet ettin.")
        oyuncu.mutluluk += 15
        oyuncu.sosyal_beceri += 10
        time.sleep(2)

def durumu_goster(oyuncu, gun):
    """Oyuncunun anlık durumunu gösterir."""
    clear_screen()
    print(f"--- GÜN: {gun} ---")
    print("--- GÜNCEL DURUM ---")
    print(f"İsim: {oyuncu.isim}  |  Yaş: {oyuncu.yas}")
    print("-" * 20)
    print(f"Sağlık: {oyuncu.saglik}/100  |  Mutluluk: {oyuncu.mutluluk}/100  |  Enerji: {oyuncu.enerji}/100")
    print(f"Açlık: {oyuncu.aclik}/100    |  Hijyen: {oyuncu.hijyen}/100")
    print("-" * 20)
    print(f"Para: {oyuncu.para} TL")
    print(f"Zeka: {oyuncu.zeka}    |  Sosyal Beceri: {oyuncu.sosyal_beceri}")
    print("-" * 20)
    print(f"Envanter: {', '.join(oyuncu.envanter) if oyuncu.envanter else 'Boş'}")
    print("--------------------")

def eylem_sec(oyuncu):
    """Oyuncunun eylem seçmesini sağlar ve sonucu uygular."""
    print("\nNe yapmak istersin?")
    print("1: Çalış")
    print("2: Uyu")
    print("3: Eğlen")
    print("4: Okula Git")
    print("5: Spor Yap")
    print("6: Alışveriş Yap")
    print("7: Kitap Oku")
    print("8: Envanteri Kullan")

    secim = input("Seçimin (1-8): ")

    if secim == '1':
        calis(oyuncu)
    elif secim == '2':
        uyu(oyuncu)
    elif secim == '3':
        eglen(oyuncu)
    elif secim == '4':
        okula_git(oyuncu)
    elif secim == '5':
        spor_yap(oyuncu)
    elif secim == '6':
        alisveris_yap(oyuncu)
    elif secim == '7':
        kitap_oku(oyuncu)
    elif secim == '8':
        envanter_kullan(oyuncu)
    else:
        print("Geçersiz seçim. Bir tur bekliyorsun.")
        time.sleep(1)

def alisveris_yap(oyuncu):
    """Alışveriş yapma eylemi."""
    print("\n--- MAĞAZA ---")
    for i, (esya, detaylar) in enumerate(magaza_esyalari.items()):
        print(f"{i+1}: {esya.capitalize()} - {detaylar['fiyat']} TL")

    try:
        secim = int(input(f"Ne almak istersin? (1-{len(magaza_esyalari)}), çıkmak için 0): "))
        if secim == 0:
            return

        secilen_esya_adi = list(magaza_esyalari.keys())[secim - 1]
        secilen_esya = magaza_esyalari[secilen_esya_adi]

        if oyuncu.para >= secilen_esya['fiyat']:
            oyuncu.para -= secilen_esya['fiyat']
            oyuncu.envanter.append(secilen_esya_adi)
            print(f"{secilen_esya_adi.capitalize()} satın aldın.")
        else:
            print("Yeterli paran yok.")
    except (ValueError, IndexError):
        print("Geçersiz seçim.")
    time.sleep(2)

def kitap_oku(oyuncu):
    """Kitap okuma eylemi."""
    if "kitap" in oyuncu.envanter:
        print("Kitap okuyarak zekanı geliştirdin.")
        oyuncu.zeka = min(100, oyuncu.zeka + magaza_esyalari["kitap"]["deger"])
        oyuncu.enerji -= 5
        oyuncu.envanter.remove("kitap") # Kitap okunduktan sonra kaybolur
    else:
        print("Okuyacak bir kitabın yok. Mağazadan alabilirsin.")
    time.sleep(2)

def envanter_kullan(oyuncu):
    """Envanterdeki bir eşyayı kullanma eylemi."""
    if not oyuncu.envanter:
        print("Envanterin boş.")
        time.sleep(2)
        return

    print("\n--- ENVANTER ---")
    for i, esya in enumerate(oyuncu.envanter):
        print(f"{i+1}: {esya.capitalize()}")

    try:
        secim = int(input(f"Ne kullanmak istersin? (1-{len(oyuncu.envanter)}), çıkmak için 0): "))
        if secim == 0:
            return

        secilen_esya_adi = oyuncu.envanter[secim - 1]
        esya_detay = magaza_esyalari[secilen_esya_adi]

        etki_alani = esya_detay['etki']
        deger = esya_detay['deger']

        # setattr kullanarak oyuncunun ilgili özelliğini dinamik olarak güncelliyoruz
        mevcut_deger = getattr(oyuncu, etki_alani)
        setattr(oyuncu, etki_alani, min(100, max(0, mevcut_deger + deger)))

        print(f"{secilen_esya_adi.capitalize()} kullandın. {etki_alani.capitalize()} {deger} değişti.")
        oyuncu.envanter.remove(secilen_esya_adi)

    except (ValueError, IndexError):
        print("Geçersiz seçim.")
    time.sleep(2)

def calis(oyuncu):
    """Çalışma eylemi."""
    if oyuncu.enerji >= 20:
        # Tecrübe ve zekaya dayalı maaş
        maas = 50 + (oyuncu.zeka // 10) + (oyuncu.is_emegi // 5)
        print(f"Bugün çalıştın ve {maas} TL kazandın.")
        oyuncu.para += maas
        oyuncu.enerji -= 20
        oyuncu.mutluluk -= 10
        oyuncu.aclik += 15
        oyuncu.hijyen -= 10
        oyuncu.is_emegi += 1

        # Terfi sistemi
        if oyuncu.is_emegi == 50:
            print("\nTebrikler! İş yerinde gösterdiğin çaba fark edildi ve terfi aldın! Maaşın arttı.")
            # Bu, gelecekte daha karmaşık işlere geçiş için bir temel olabilir.
            oyuncu.zeka += 5 # Terfi bonusu
            time.sleep(2)

    else:
        print("Çok yorgunsun, çalışamazsın. Biraz dinlenmelisin.")
    time.sleep(2)

def uyu(oyuncu):
    """Uyuma eylemi."""
    print("İyi bir uyku çektin.")
    oyuncu.enerji = min(100, oyuncu.enerji + 50)
    oyuncu.aclik += 5
    time.sleep(2)

def eglen(oyuncu):
    """Eğlenme eylemi."""
    if oyuncu.para >= 30:
        print("Dışarı çıkıp eğlendin, keyfin yerine geldi!")
        oyuncu.mutluluk = min(100, oyuncu.mutluluk + 30)
        oyuncu.enerji -= 15
        oyuncu.para -= 30
        oyuncu.sosyal_beceri += 5
    else:
        print("Eğlenmek için yeterli paran yok.")
    time.sleep(2)

def okula_git(oyuncu):
    """Okula gitme eylemi."""
    if oyuncu.enerji >= 15 and oyuncu.para >= 50:
        print("Okula gittin ve yeni şeyler öğrendin.")
        oyuncu.zeka = min(100, oyuncu.zeka + 10)
        oyuncu.enerji -= 15
        oyuncu.para -= 50
        oyuncu.mutluluk -= 5
    elif oyuncu.enerji < 15:
        print("Okula gidemeyecek kadar yorgunsun.")
    else:
        print("Okul masrafları için yeterli paran yok.")
    time.sleep(2)

def spor_yap(oyuncu):
    """Spor yapma eylemi."""
    if oyuncu.enerji >= 25:
        print("Spor yaptın, sağlığın ve enerjin arttı!")
        oyuncu.saglik = min(100, oyuncu.saglik + 10)
        oyuncu.enerji -= 25
        oyuncu.mutluluk += 10
        oyuncu.aclik += 10
    else:
        print("Spor yapamayacak kadar yorgunsun.")
    time.sleep(2)

if __name__ == "__main__":
    main()
