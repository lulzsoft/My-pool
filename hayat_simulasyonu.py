# -*- coding: utf-8 -*-

import random
import os
import time

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Isletme:
    def __init__(self, isim, sermaye):
        self.isim = isim
        self.sermaye = sermaye
        self.gelir = 0
        self.gider = 50 # Sabit giderler
        self.calisan_sayisi = 1
        self.musteri_memnuniyeti = 70

    def gunluk_guncelle(self):
        """İşletmenin günlük gelir ve giderlerini hesaplar."""
        self.gider = 50 + (self.calisan_sayisi * 30) # Çalışan maaşları
        # Gelir; sermaye, çalışan sayısı ve memnuniyete bağlı
        self.gelir = (self.sermaye // 100) + (self.calisan_sayisi * 10) * (self.musteri_memnuniyeti / 100)
        net_kar = self.gelir - self.gider
        return int(net_kar)

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
        self.portfoy = {} # Yatırım portföyü
        self.isletme = None # Oyuncunun sahip olduğu işletme

piyasa = {
    "hisse_senedi_A": {"fiyat": 100, "trend": 0.1, "volatilite": 0.5},
    "emlak": {"fiyat": 5000, "trend": 0.05, "volatilite": 0.2}
}

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
    saat = 8 # Oyuna sabah 8'de başla
    while not oyun_bitti:
        zaman = {"gun": gun, "saat": saat}
        durumu_goster(oyuncu, zaman)
        harcanan_saat = eylem_sec(oyuncu)

        # Zamanı ilerlet
        for _ in range(harcanan_saat):
            saat += 1
            saati_ilerlet(oyuncu, saat)
            if saat >= 24:
                saat = 0
                gun += 1
                piyasayi_guncelle() # Her yeni günde piyasayı güncelle
                if oyuncu.isletme:
                    gunluk_kar = oyuncu.isletme.gunluk_guncelle()
                    oyuncu.para += gunluk_kar
                    print(f"\nİşletmen bugün {gunluk_kar} TL {'kar' if gunluk_kar >= 0 else 'zarar'} etti.")
                    time.sleep(1)
                # Yaşlanma kontrolü
                if gun % 365 == 0:
                    oyuncu.yas += 1
                    print(f"\nDoğum günün kutlu olsun! Artık {oyuncu.yas} yaşındasın.")
                    time.sleep(2)

        if oyuncu.saglik <= 0:
            oyun_bitti = True
            print("\nSağlığın tükendi ve hayatını kaybettin. Oyun bitti.")

def saati_ilerlet(oyuncu, saat):
    """Zamanı bir saat ilerletir ve statları günceller."""
    # Her saat başı ihtiyaçlar hafifçe artar/azalır
    oyuncu.aclik = min(100, oyuncu.aclik + 1)
    oyuncu.hijyen = max(0, oyuncu.hijyen - 0.5)

    # Belirli saatlerde özel durumlar
    if saat == 22: # Uyku zamanı geldi
        oyuncu.enerji -= 5
        print("\nUykun geliyor...")
        time.sleep(0.5)

    if oyuncu.aclik >= 80 and saat % 2 == 0: # Açlık krizi
        oyuncu.saglik -= 1
        oyuncu.mutluluk -= 1
        print("\nKarnın gurulduyor, sağlığın ve mutluluğun azalıyor.")
        time.sleep(0.5)

def piyasayi_guncelle():
    """Piyasadaki varlıkların fiyatlarını günceller."""
    for varlik, detaylar in piyasa.items():
        degisim_yuzdesi = detaylar["trend"] + (random.uniform(-detaylar["volatilite"], detaylar["volatilite"]))
        eski_fiyat = detaylar["fiyat"]
        yeni_fiyat = eski_fiyat * (1 + degisim_yuzdesi)
        piyasa[varlik]["fiyat"] = max(1, int(yeni_fiyat)) # Fiyatın 1'in altına düşmesini engelle
    print("\n--- Piyasa Güncellendi ---")
    time.sleep(1)

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

def durumu_goster(oyuncu, zaman):
    """Oyuncunun anlık durumunu gösterir."""
    clear_screen()
    print(f"--- GÜN: {zaman['gun']} | SAAT: {zaman['saat']:02d}:00 ---")
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

    portfoy_degeri = 0
    portfoy_metni = []
    if oyuncu.portfoy:
        for varlik, adet in oyuncu.portfoy.items():
            anlik_deger = piyasa[varlik]['fiyat'] * adet
            portfoy_degeri += anlik_deger
            portfoy_metni.append(f"{varlik.replace('_', ' ').title()} ({adet} adet)")
    print(f"Portföy: {', '.join(portfoy_metni) if portfoy_metni else 'Boş'} (Toplam Değer: {portfoy_degeri} TL)")

    if oyuncu.isletme:
        isletme = oyuncu.isletme
        print("-" * 20)
        print(f"İşletme: {isletme.isim} | Sermaye: {isletme.sermaye} TL | Müşteri Memnuniyeti: {isletme.musteri_memnuniyeti}%")

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
    print("9: Yatırım Yap")
    print("10: İş Kur / Yönet")

    secim = input("Seçimin (1-10): ")

    if secim == '1':
        return calis(oyuncu)
    elif secim == '2':
        return uyu(oyuncu)
    elif secim == '3':
        return eglen(oyuncu)
    elif secim == '4':
        return okula_git(oyuncu)
    elif secim == '5':
        return spor_yap(oyuncu)
    elif secim == '6':
        return alisveris_yap(oyuncu)
    elif secim == '7':
        return kitap_oku(oyuncu)
    elif secim == '8':
        return envanter_kullan(oyuncu)
    elif secim == '9':
        return yatirim_yap(oyuncu)
    elif secim == '10':
        if oyuncu.isletme is None:
            return is_kur(oyuncu)
        else:
            return isletmeyi_yonet(oyuncu)
    else:
        print("Geçersiz seçim. 1 saatin boşa geçti.")
        time.sleep(1)
        return 1 # Geçersiz seçim 1 saat harcar

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
    return 1 # Alışveriş 1 saat sürer

def kitap_oku(oyuncu):
    """Kitap okuma eylemi."""
    if "kitap" in oyuncu.envanter:
        print("1 saat kitap okuyarak zekanı geliştirdin.")
        oyuncu.zeka = min(100, oyuncu.zeka + magaza_esyalari["kitap"]["deger"])
        oyuncu.enerji -= 5
        oyuncu.mutluluk += 5
        oyuncu.envanter.remove("kitap") # Kitap okunduktan sonra kaybolur
        time.sleep(2)
        return 1
    else:
        print("Okuyacak bir kitabın yok. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

def envanter_kullan(oyuncu):
    """Envanterdeki bir eşyayı kullanma eylemi."""
    if not oyuncu.envanter:
        print("Envanterin boş. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

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
    return 1 # Envanter kullanımı 1 saat sürer

def calis(oyuncu):
    """Çalışma eylemi."""
    if oyuncu.enerji >= 40:
        saat = 8
        kazanc_per_saat = 10 + (oyuncu.zeka // 10) + (oyuncu.is_emegi // 10)
        toplam_kazanc = kazanc_per_saat * saat
        print(f"{saat} saat çalıştın ve {toplam_kazanc} TL kazandın.")
        oyuncu.para += toplam_kazanc
        oyuncu.enerji -= 40
        oyuncu.mutluluk -= 15
        oyuncu.is_emegi += saat

        if oyuncu.is_emegi >= 200: # Terfi için gereken tecrübe
            print("\nTebrikler! Terfi aldın! Saatlik ücretin arttı.")
            # Burada daha karmaşık terfi mekanikleri eklenebilir.

        time.sleep(2)
        return saat
    else:
        print("Çok yorgunsun, tam gün çalışamazsın. Sadece 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

def uyu(oyuncu):
    """Uyuma eylemi."""
    saat = int(input("Kaç saat uyumak istersin? (1-10): "))
    saat = max(1, min(10, saat)) # 1 ile 10 saat arası sınırla
    print(f"{saat} saat uyudun.")
    oyuncu.enerji = min(100, oyuncu.enerji + saat * 8) # Saatte 8 enerji
    time.sleep(2)
    return saat

def eglen(oyuncu):
    """Eğlenme eylemi."""
    if oyuncu.para >= 30:
        print("Dışarı çıkıp 2 saat eğlendin, keyfin yerine geldi!")
        oyuncu.mutluluk = min(100, oyuncu.mutluluk + 20)
        oyuncu.enerji -= 10
        oyuncu.para -= 30
        oyuncu.sosyal_beceri += 5
        time.sleep(2)
        return 2
    else:
        print("Eğlenmek için yeterli paran yok. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

def okula_git(oyuncu):
    """Okula gitme eylemi."""
    if oyuncu.enerji >= 20 and oyuncu.para >= 50:
        print("Okula gidip 4 saat ders çalıştın.")
        oyuncu.zeka = min(100, oyuncu.zeka + 5)
        oyuncu.enerji -= 20
        oyuncu.para -= 50
        oyuncu.mutluluk -= 10
        time.sleep(2)
        return 4
    elif oyuncu.enerji < 20:
        print("Okula gidemeyecek kadar yorgunsun. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1
    else:
        print("Okul masrafları için yeterli paran yok. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

def spor_yap(oyuncu):
    """Spor yapma eylemi."""
    if oyuncu.enerji >= 25:
        print("1 saat spor yaptın, sağlığın ve enerjin arttı!")
        oyuncu.saglik = min(100, oyuncu.saglik + 5)
        oyuncu.enerji -= 25
        oyuncu.mutluluk += 10
        time.sleep(2)
        return 1
    else:
        print("Spor yapamayacak kadar yorgunsun. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

def yatirim_yap(oyuncu):
    """Yatırım yapma eylemi."""
    print("\n--- YATIRIM MERKEZİ ---")
    print("1: Varlık Al")
    print("2: Varlık Sat")
    secim = input("Ne yapmak istersin? (1-2), çıkmak için 0): ")

    if secim == '1':
        print("\n--- PİYASA (ALIM) ---")
        for i, (varlik, detaylar) in enumerate(piyasa.items()):
            print(f"{i+1}: {varlik.replace('_', ' ').title()} - {detaylar['fiyat']} TL")

        try:
            varlik_secim = int(input(f"Ne almak istersin? (1-{len(piyasa)}): "))
            adet = int(input("Kaç adet almak istersin?: "))

            secilen_varlik_adi = list(piyasa.keys())[varlik_secim - 1]
            fiyat = piyasa[secilen_varlik_adi]['fiyat']
            toplam_tutar = fiyat * adet

            if oyuncu.para >= toplam_tutar:
                oyuncu.para -= toplam_tutar
                oyuncu.portfoy[secilen_varlik_adi] = oyuncu.portfoy.get(secilen_varlik_adi, 0) + adet
                print(f"{adet} adet {secilen_varlik_adi.replace('_', ' ').title()} satın aldın.")
            else:
                print("Yeterli paran yok.")

        except (ValueError, IndexError):
            print("Geçersiz seçim.")

    elif secim == '2':
        if not oyuncu.portfoy:
            print("Satacak hiçbir varlığın yok.")
        else:
            print("\n--- PORTFÖY (SATIM) ---")
            portfoy_listesi = list(oyuncu.portfoy.keys())
            for i, varlik in enumerate(portfoy_listesi):
                adet = oyuncu.portfoy[varlik]
                mevcut_fiyat = piyasa[varlik]['fiyat']
                print(f"{i+1}: {varlik.replace('_', ' ').title()} ({adet} adet) - Mevcut Fiyat: {mevcut_fiyat} TL")

            try:
                varlik_secim = int(input(f"Ne satmak istersin? (1-{len(portfoy_listesi)}): "))
                adet_satis = int(input("Kaç adet satmak istersin?: "))

                secilen_varlik_adi = portfoy_listesi[varlik_secim - 1]

                if adet_satis <= oyuncu.portfoy[secilen_varlik_adi]:
                    fiyat = piyasa[secilen_varlik_adi]['fiyat']
                    toplam_kazanc = fiyat * adet_satis
                    oyuncu.para += toplam_kazanc
                    oyuncu.portfoy[secilen_varlik_adi] -= adet_satis
                    if oyuncu.portfoy[secilen_varlik_adi] == 0:
                        del oyuncu.portfoy[secilen_varlik_adi]
                    print(f"{adet_satis} adet {secilen_varlik_adi.replace('_', ' ').title()} sattın ve {toplam_kazanc} TL kazandın.")
                else:
                    print("Elinde o kadar varlık yok.")

            except (ValueError, IndexError):
                print("Geçersiz seçim.")

    time.sleep(2)
    return 2 # Yatırım işlemi 2 saat sürer

def is_kur(oyuncu):
    """Yeni bir iş kurma eylemi."""
    kurulum_maliyeti = 2500
    print(f"\nKendi işini kurmak için gereken başlangıç sermayesi {kurulum_maliyeti} TL.")
    secim = input("İş kurmak istiyor musun? (e/h): ").lower()

    if secim == 'e':
        if oyuncu.para >= kurulum_maliyeti:
            isletme_ismi = input("İşletmenin adı ne olsun?: ")
            oyuncu.para -= kurulum_maliyeti
            oyuncu.isletme = Isletme(isletme_ismi, kurulum_maliyeti)
            print(f"Tebrikler! '{isletme_ismi}' adında kendi işletmeni kurdun.")
        else:
            print("Yeterli paran yok.")
    time.sleep(2)
    return 3 # İş kurma planlaması 3 saat sürer

def isletmeyi_yonet(oyuncu):
    """Mevcut işletmeyi yönetme eylemi."""
    isletme = oyuncu.isletme
    print(f"\n--- {isletme.isim.upper()} YÖNETİM PANELİ ---")
    print(f"Sermaye: {isletme.sermaye} TL | Çalışan Sayısı: {isletme.calisan_sayisi} | Müşteri Memnuniyeti: {isletme.musteri_memnuniyeti}%")
    print("1: Sermaye Ekle")
    print("2: Çalışan İşe Al (Maliyet: 500 TL)")
    print("3: Çalışan Kov")
    print("4: Pazarlama Yap (Maliyet: 300 TL)")
    print("5: İşletmeyi Sat")

    secim = input("Ne yapmak istersin? (1-5), çıkmak için 0): ")

    if secim == '1':
        try:
            miktar = int(input("Ne kadar sermaye eklemek istersin?: "))
            if oyuncu.para >= miktar:
                oyuncu.para -= miktar
                isletme.sermaye += miktar
                print(f"İşletmeye {miktar} TL sermaye eklendi.")
            else:
                print("Yeterli paran yok.")
        except ValueError:
            print("Geçersiz miktar.")

    elif secim == '2':
        if oyuncu.para >= 500:
            oyuncu.para -= 500
            isletme.calisan_sayisi += 1
            isletme.musteri_memnuniyeti -= 5 # Yeni çalışanların adaptasyonu
            print("Yeni bir çalışan işe aldın.")
        else:
            print("İşe alım maliyeti için yeterli paran yok.")

    elif secim == '3':
        if isletme.calisan_sayisi > 1:
            isletme.calisan_sayisi -= 1
            isletme.musteri_memnuniyeti += 10 # Daha az çalışanla daha iyi odaklanma
            print("Bir çalışanı işten çıkardın.")
        else:
            print("Tek çalışanı kovamazsın, o sensin!")

    elif secim == '4':
        if oyuncu.para >= 300:
            oyuncu.para -= 300
            isletme.musteri_memnuniyeti = min(100, isletme.musteri_memnuniyeti + 15)
            print("Pazarlama kampanyası müşteri memnuniyetini artırdı.")
        else:
            print("Pazarlama için yeterli paran yok.")

    elif secim == '5':
        satis_degeri = isletme.sermaye + (isletme.gelir * 5) - (isletme.gider * 2)
        satis_degeri = max(0, int(satis_degeri))
        print(f"İşletmenin tahmini satış değeri: {satis_degeri} TL.")
        onay = input("İşletmeyi bu fiyata satmak istediğine emin misin? (e/h): ").lower()
        if onay == 'e':
            oyuncu.para += satis_degeri
            oyuncu.isletme = None
            print("İşletmeyi başarıyla sattın!")

    time.sleep(2)
    return 4 # Yönetim 4 saat sürer

if __name__ == "__main__":
    main()
