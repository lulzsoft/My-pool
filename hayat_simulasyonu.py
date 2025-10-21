# -*- coding: utf-8 -*-

import random
import os
import time

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Calisan:
    def __init__(self):
        self.yetenek = random.randint(5, 15) # 5-15 arası başlangıç yeteneği
        self.moral = 70
        self.maas = 30 # Standart günlük maaş

class Isletme:
    def __init__(self, isim, sermaye, urun_tipi):
        self.isim = isim
        self.sermaye = sermaye
        self.urun_tipi = urun_tipi # "elektronik", "gıda" vb.
        self.calisanlar = [Calisan()] # İşletme bir çalışanla başlar (kurucu)
        self.musteri_memnuniyeti = 70
        self.ar_ge_seviyesi = 1
        self.hammadde_envanteri = {"hammadde": 0, "elektronik": 0, "gıda": 0}
        self.urun_envanteri = 0 # Üretilmiş bitmiş ürün sayısı

    @property
    def calisan_sayisi(self):
        return len(self.calisanlar)

    def gunluk_guncelle(self, piyasa):
        """İşletmenin günlük üretim, satış ve kar/zarar durumunu günceller."""
        # Üretim
        toplam_yetenek = sum(c.yetenek for c in self.calisanlar)
        uretim_kapasitesi = int((toplam_yetenek / 10) * self.ar_ge_seviyesi)
        uretilebilecek_miktar = uretim_kapasitesi

        # Gerekli hammaddeleri kontrol et
        if self.urun_tipi == "elektronik":
            gerekli_hammadde1 = "hammadde"
            gerekli_hammadde2 = "elektronik"
            if self.hammadde_envanteri[gerekli_hammadde1] >= uretim_kapasitesi and self.hammadde_envanteri[gerekli_hammadde2] >= uretim_kapasitesi:
                self.hammadde_envanteri[gerekli_hammadde1] -= uretim_kapasitesi
                self.hammadde_envanteri[gerekli_hammadde2] -= uretim_kapasitesi
                self.urun_envanteri += uretilebilecek_miktar
                print(f"\n{self.isim}, {uretilebilecek_miktar} adet {self.urun_tipi} üretti.")
            else:
                print(f"\nÜretim için yeterli hammadde yok!")
                uretilebilecek_miktar = 0

        # Satış
        satilabilecek_miktar = int(self.urun_envanteri * (self.musteri_memnuniyeti / 100))
        urun_fiyati = piyasa.ticari_mallar[self.urun_tipi]["fiyat"] * 1.5 # %50 kar marjı
        gelir = satilabilecek_miktar * urun_fiyati
        self.urun_envanteri -= satilabilecek_miktar

        # Giderler
        toplam_maas = sum(c.maas for c in self.calisanlar)
        gider = 50 + toplam_maas # Sabit giderler ve maaşlar

        net_kar = gelir - gider
        return int(net_kar)

class ZamanSistemi:
    def __init__(self):
        self.gun = 1
        self.saat = 8 # Oyuna sabah 8'de başla

    def __str__(self):
        return f"GÜN: {self.gun} | SAAT: {self.saat:02d}:00"

class PiyasaSistemi:
    def __init__(self):
        self.yatirim_mallari = {
            "hisse_senedi_A": {"fiyat": 100, "trend": 0.1, "volatilite": 0.5},
            "emlak": {"fiyat": 5000, "trend": 0.05, "volatilite": 0.2}
        }
        self.ticari_mallar = {
            "elektronik": {"fiyat": 500, "arz": 100, "talep": 100, "volatilite": 0.3},
            "gıda": {"fiyat": 50, "arz": 1000, "talep": 1000, "volatilite": 0.1},
            "hammadde": {"fiyat": 200, "arz": 500, "talep": 500, "volatilite": 0.5}
        }

    def gunluk_guncelle(self):
        """Piyasadaki tüm varlıkların fiyatlarını günceller."""
        for varlik, detaylar in self.yatirim_mallari.items():
            degisim_yuzdesi = detaylar["trend"] + (random.uniform(-detaylar["volatilite"], detaylar["volatilite"]))
            eski_fiyat = detaylar["fiyat"]
            yeni_fiyat = eski_fiyat * (1 + degisim_yuzdesi)
            self.yatirim_mallari[varlik]["fiyat"] = max(1, int(yeni_fiyat))

        for mal, detaylar in self.ticari_mallar.items():
            # Arz ve talebi hafifçe dalgalandır
            detaylar["arz"] += random.randint(-10, 10)
            detaylar["talep"] += random.randint(-5, 5)
            detaylar["arz"] = max(10, detaylar["arz"]) # Sıfıra düşmesini engelle
            detaylar["talep"] = max(10, detaylar["talep"])

            # Fiyatı arz-talep dengesine göre ayarla
            fiyat_degisim_orani = (detaylar["talep"] - detaylar["arz"]) / 1000 # Fiyat değişim hassasiyeti
            fiyat_degisimi = detaylar["fiyat"] * fiyat_degisim_orani
            yeni_fiyat = detaylar["fiyat"] + fiyat_degisimi
            self.ticari_mallar[mal]["fiyat"] = max(5, int(yeni_fiyat)) # Min fiyat

        print("\n--- Piyasa Güncellendi ---")
        time.sleep(1)

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
        self.ticari_envanter = {} # Ticari mallar için envanter
        self.isletme = None # Oyuncunun sahip olduğu işletme
        self.metabolizma_hizi = 1.0
        self.metabolizma_etki_suresi = 0

magaza_esyalari = {
    "kitap": {"fiyat": 75, "etki": "zeka", "deger": 5},
    "konsol oyunu": {"fiyat": 200, "etki": "mutluluk", "deger": 15},
    "abur cubur": {"fiyat": 15, "etki": "aclik", "deger": -40, "metabolizma_etkisi": 0.2},
    "ev yemeği": {"fiyat": 40, "etki": "aclik", "deger": -50, "metabolizma_etkisi": 0},
    "lüks restoran yemeği": {"fiyat": 150, "etki": "aclik", "deger": -70, "metabolizma_etkisi": -0.1},
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
    zaman = ZamanSistemi()
    piyasa = PiyasaSistemi()
    while not oyun_bitti:
        durumu_goster(oyuncu, zaman, piyasa)
        harcanan_saat = eylem_sec(oyuncu, piyasa)

        # Zamanı ilerlet
        for _ in range(harcanan_saat):
            zaman.saat += 1
            saati_ilerlet(oyuncu, zaman.saat)
            if zaman.saat >= 24:
                zaman.saat = 0
                zaman.gun += 1
                piyasa.gunluk_guncelle() # Her yeni günde piyasayı güncelle
                if oyuncu.isletme:
                    gunluk_kar = oyuncu.isletme.gunluk_guncelle(piyasa)
                    oyuncu.para += gunluk_kar
                    print(f"\nİşletmen bugün {gunluk_kar} TL {'kar' if gunluk_kar >= 0 else 'zarar'} etti.")
                    time.sleep(1)
                # Yaşlanma kontrolü
                if zaman.gun % 365 == 0:
                    oyuncu.yas += 1
                    print(f"\nDoğum günün kutlu olsun! Artık {oyuncu.yas} yaşındasın.")
                    time.sleep(2)

        if oyuncu.saglik <= 0:
            oyun_bitti = True
            print("\nSağlığın tükendi ve hayatını kaybettin. Oyun bitti.")

def saati_ilerlet(oyuncu, saat):
    """Zamanı bir saat ilerletir ve statları günceller."""
    # Metabolizma etkisini yönet
    if oyuncu.metabolizma_etki_suresi > 0:
        oyuncu.metabolizma_etki_suresi -= 1
        if oyuncu.metabolizma_etki_suresi == 0:
            oyuncu.metabolizma_hizi = 1.0
            print("\nMetabolizman normale döndü.")
            time.sleep(1)

    # Her saat başı ihtiyaçlar hafifçe artar/azalır
    oyuncu.aclik = min(100, oyuncu.aclik + (1 * oyuncu.metabolizma_hizi))
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

def durumu_goster(oyuncu, zaman, piyasa):
    """Oyuncunun anlık durumunu gösterir."""
    clear_screen()
    print(f"--- {zaman} ---")
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
            anlik_deger = piyasa.yatirim_mallari[varlik]['fiyat'] * adet
            portfoy_degeri += anlik_deger
            portfoy_metni.append(f"{varlik.replace('_', ' ').title()} ({adet} adet)")
    print(f"Portföy: {', '.join(portfoy_metni) if portfoy_metni else 'Boş'} (Toplam Değer: {portfoy_degeri} TL)")

    ticari_envanter_metni = [f"{mal.capitalize()} ({adet} adet)" for mal, adet in oyuncu.ticari_envanter.items()]
    print(f"Ticari Envanter: {', '.join(ticari_envanter_metni) if ticari_envanter_metni else 'Boş'}")

    if oyuncu.isletme:
        isletme = oyuncu.isletme
        print("-" * 20)
        print(f"İşletme: {isletme.isim} | Sermaye: {isletme.sermaye} TL | Müşteri Memnuniyeti: {isletme.musteri_memnuniyeti}%")

    print("--------------------")

def eylem_sec(oyuncu, piyasa):
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
    print("11: Ticaret Yap")

    secim = input("Seçimin (1-11): ")

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
        return yatirim_yap(oyuncu, piyasa)
    elif secim == '10':
        if oyuncu.isletme is None:
            return is_kur(oyuncu)
        else:
            return isletmeyi_yonet(oyuncu, piyasa)
    elif secim == '11':
        return ticaret_yap(oyuncu, piyasa)
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
            return 1

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
            return 1

        secilen_esya_adi = oyuncu.envanter[secim - 1]
        esya_detay = magaza_esyalari[secilen_esya_adi]

        etki_alani = esya_detay['etki']
        deger = esya_detay['deger']

        # setattr kullanarak oyuncunun ilgili özelliğini dinamik olarak güncelliyoruz
        mevcut_deger = getattr(oyuncu, etki_alani)
        setattr(oyuncu, etki_alani, min(100, max(0, mevcut_deger + deger)))

        # Metabolizma etkisini uygula
        if "metabolizma_etkisi" in esya_detay:
            oyuncu.metabolizma_hizi = 1.0 + esya_detay["metabolizma_etkisi"]
            oyuncu.metabolizma_etki_suresi = 4 # Etki 4 saat sürer
            print(f"Yediğin yiyecek metabolizmanı etkiledi! Mevcut hız: {oyuncu.metabolizma_hizi}x")

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

def yatirim_yap(oyuncu, piyasa):
    """Yatırım yapma eylemi."""
    print("\n--- YATIRIM MERKEZİ ---")
    print("1: Varlık Al")
    print("2: Varlık Sat")
    secim = input("Ne yapmak istersin? (1-2), çıkmak için 0): ")

    if secim == '1':
        print("\n--- PİYASA (ALIM) ---")
        for i, (varlik, detaylar) in enumerate(piyasa.yatirim_mallari.items()):
            print(f"{i+1}: {varlik.replace('_', ' ').title()} - {detaylar['fiyat']} TL")

        try:
            varlik_secim = int(input(f"Ne almak istersin? (1-{len(piyasa.yatirim_mallari)}): "))
            adet = int(input("Kaç adet almak istersin?: "))

            secilen_varlik_adi = list(piyasa.yatirim_mallari.keys())[varlik_secim - 1]
            fiyat = piyasa.yatirim_mallari[secilen_varlik_adi]['fiyat']
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
                mevcut_fiyat = piyasa.yatirim_mallari[varlik]['fiyat']
                print(f"{i+1}: {varlik.replace('_', ' ').title()} ({adet} adet) - Mevcut Fiyat: {mevcut_fiyat} TL")

            try:
                varlik_secim = int(input(f"Ne satmak istersin? (1-{len(portfoy_listesi)}): "))
                adet_satis = int(input("Kaç adet satmak istersin?: "))

                secilen_varlik_adi = portfoy_listesi[varlik_secim - 1]

                if adet_satis <= oyuncu.portfoy[secilen_varlik_adi]:
                    fiyat = piyasa.yatirim_mallari[secilen_varlik_adi]['fiyat']
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
    print("Hangi alanda bir iş kurmak istersin?")
    # Şimdilik sadece elektronik üretimi mevcut, gelecekte genişletilebilir.
    print("1: Elektronik")
    secim = input("Seçimin (1): ")

    if secim == '1':
        urun_tipi = "elektronik"
        if oyuncu.para >= kurulum_maliyeti:
            isletme_ismi = input("İşletmenin adı ne olsun?: ")
            oyuncu.para -= kurulum_maliyeti
            oyuncu.isletme = Isletme(isletme_ismi, kurulum_maliyeti, urun_tipi)
            print(f"Tebrikler! '{isletme_ismi}' adında bir {urun_tipi} şirketi kurdun.")
        else:
            print("Yeterli paran yok.")
    else:
        print("Geçersiz seçim.")
    time.sleep(2)
    return 3 # İş kurma planlaması 3 saat sürer

def isletmeyi_yonet(oyuncu, piyasa):
    """Mevcut işletmeyi yönetme eylemi."""
    isletme = oyuncu.isletme
    print(f"\n--- {isletme.isim.upper()} YÖNETİM PANELİ ---")
    print(f"Sermaye: {isletme.sermaye} TL | Çalışanlar: {isletme.calisan_sayisi} | Müşteri Memnuniyeti: {isletme.musteri_memnuniyeti}%")
    hammadde_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in isletme.hammadde_envanteri.items() if v > 0])
    print(f"Hammadde Envanteri: {hammadde_str if hammadde_str else 'Boş'}")
    print(f"Ürün Envanteri: {isletme.urun_envanteri} adet {isletme.urun_tipi}")
    print("-" * 20)
    print("--- İNSAN KAYNAKLARI ---")
    print("1: Çalışanları Listele")
    print("2: Çalışan İşe Al (Maliyet: 500 TL)")
    print("3: Çalışan Kov")
    print("4: Çalışanlara Eğitim Ver (Maliyet: 1000 TL)")
    print("5: Sosyal Etkinlik Düzenle (Maliyet: 750 TL)")
    print("--- FİNANS VE PAZARLAMA ---")
    print("6: Sermaye Ekle")
    print("7: Pazarlama Yap (Maliyet: 300 TL)")
    print("8: Hammadde Satın Al")
    print("--- İŞ GELİŞTİRME ---")
    print("9: Ar-Ge Yatırımı Yap (Maliyet: 2000 TL)")
    print("10: İşletmeyi Sat")

    secim = input("Ne yapmak istersin? (1-10), çıkmak için 0): ")

    if secim == '1':
        print("\n--- ÇALIŞAN LİSTESİ ---")
        for i, calisan in enumerate(isletme.calisanlar):
            print(f"Çalışan {i+1}: Yetenek: {calisan.yetenek}, Moral: {calisan.moral}, Maaş: {calisan.maas} TL")

    elif secim == '2':
        if oyuncu.para >= 500:
            oyuncu.para -= 500
            isletme.calisanlar.append(Calisan())
            print("Yeni bir çalışan işe aldın.")
        else:
            print("İşe alım maliyeti için yeterli paran yok.")

    elif secim == '3':
        if isletme.calisan_sayisi > 1:
            # Şimdilik en kötü çalışanı kovar (en düşük yetenekli)
            isletme.calisanlar.sort(key=lambda c: c.yetenek)
            isletme.calisanlar.pop(0)
            print("En düşük yetenekli çalışan işten çıkarıldı.")
        else:
            print("Tek çalışanı kovamazsın, o sensin!")

    elif secim == '4':
        if isletme.sermaye >= 1000:
            isletme.sermaye -= 1000
            for calisan in isletme.calisanlar:
                calisan.yetenek += random.randint(1, 3)
            print("Tüm çalışanlara eğitim verildi, yetenekleri arttı.")
        else:
            print("Eğitim için işletmenin yeterli sermayesi yok.")

    elif secim == '5':
        if isletme.sermaye >= 750:
            isletme.sermaye -= 750
            for calisan in isletme.calisanlar:
                calisan.moral = min(100, calisan.moral + 15)
            print("Sosyal etkinlik düzenlendi, çalışanların morali yükseldi.")
        else:
            print("Etkinlik için işletmenin yeterli sermayesi yok.")

    elif secim == '6':
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

    elif secim == '7':
        if oyuncu.para >= 300:
            oyuncu.para -= 300
            isletme.musteri_memnuniyeti = min(100, isletme.musteri_memnuniyeti + 15)
            print("Pazarlama kampanyası müşteri memnuniyetini artırdı.")
        else:
            print("Pazarlama için yeterli paran yok.")

    elif secim == '8':
        print("\n--- HAMMADDE PAZARI ---")
        for i, (mal, detaylar) in enumerate(piyasa.ticari_mallar.items()):
            print(f"{i+1}: {mal.capitalize()} - {detaylar['fiyat']} TL")

        try:
            mal_secim = int(input(f"Ne almak istersin? (1-{len(piyasa.ticari_mallar)}): "))
            adet = int(input("Kaç adet almak istersin?: "))

            secilen_mal_adi = list(piyasa.ticari_mallar.keys())[mal_secim - 1]
            fiyat = piyasa.ticari_mallar[secilen_mal_adi]['fiyat']
            toplam_tutar = fiyat * adet

            if isletme.sermaye >= toplam_tutar:
                isletme.sermaye -= toplam_tutar
                isletme.hammadde_envanteri[secilen_mal_adi] = isletme.hammadde_envanteri.get(secilen_mal_adi, 0) + adet
                print(f"İşletme için {adet} adet {secilen_mal_adi.capitalize()} satın aldın.")
            else:
                print("İşletmenin yeterli sermayesi yok.")
        except (ValueError, IndexError):
            print("Geçersiz seçim.")

    elif secim == '9':
        if isletme.sermaye >= 2000:
            isletme.sermaye -= 2000
            isletme.ar_ge_seviyesi += 1
            print(f"Ar-Ge yatırımı yapıldı! İşletmenin teknoloji seviyesi {isletme.ar_ge_seviyesi}'e yükseldi.")
        else:
            print("Ar-Ge yatırımı için işletmenin yeterli sermayesi yok.")

    elif secim == '10':
        satis_degeri = isletme.sermaye # Basit hesaplama, daha sonra detaylandırılabilir
        print(f"İşletmenin tahmini satış değeri: {satis_degeri} TL.")
        onay = input("İşletmeyi bu fiyata satmak istediğine emin misin? (e/h): ").lower()
        if onay == 'e':
            oyuncu.para += satis_degeri
            oyuncu.isletme = None
            print("İşletmeyi başarıyla sattın!")

    time.sleep(2)
    return 4 # Yönetim 4 saat sürer

def ticaret_yap(oyuncu, piyasa):
    """Ticari mal alıp satma eylemi."""
    print("\n--- TİCARET MERKEZİ ---")
    print("1: Mal Al")
    print("2: Mal Sat")
    secim = input("Ne yapmak istersin? (1-2), çıkmak için 0): ")

    # Zeka ve sosyal beceriye dayalı bonuslar
    zeka_bonusu = 1 - (oyuncu.zeka / 500) # Max %20 indirim
    sosyal_beceri_bonusu = 1 + (oyuncu.sosyal_beceri / 500) # Max %20 zam

    if secim == '1':
        print("\n--- PİYASA (MAL ALIM) ---")
        for i, (mal, detaylar) in enumerate(piyasa.ticari_mallar.items()):
            uygulanacak_fiyat = int(detaylar['fiyat'] * zeka_bonusu)
            print(f"{i+1}: {mal.capitalize()} - {uygulanacak_fiyat} TL (Piyasa: {detaylar['fiyat']} TL)")

        try:
            mal_secim = int(input(f"Ne almak istersin? (1-{len(piyasa.ticari_mallar)}): "))
            adet = int(input("Kaç adet almak istersin?: "))

            secilen_mal_adi = list(piyasa.ticari_mallar.keys())[mal_secim - 1]
            fiyat = int(piyasa.ticari_mallar[secilen_mal_adi]['fiyat'] * zeka_bonusu)
            lojistik_maliyeti = adet * 2 # Birim başına 2 TL taşıma maliyeti
            toplam_tutar = (fiyat * adet) + lojistik_maliyeti

            if oyuncu.para >= toplam_tutar:
                oyuncu.para -= toplam_tutar
                oyuncu.ticari_envanter[secilen_mal_adi] = oyuncu.ticari_envanter.get(secilen_mal_adi, 0) + adet
                piyasa.ticari_mallar[secilen_mal_adi]['talep'] += adet / 10 # Alım talebi artırır
                print(f"{adet} adet {secilen_mal_adi.capitalize()} satın aldın. Lojistik Maliyeti: {lojistik_maliyeti} TL.")
            else:
                print("Yeterli paran yok.")

        except (ValueError, IndexError):
            print("Geçersiz seçim.")

    elif secim == '2':
        if not oyuncu.ticari_envanter:
            print("Satacak hiçbir ticari malın yok.")
        else:
            print("\n--- TİCARİ ENVANTER (MAL SATIM) ---")
            envanter_listesi = list(oyuncu.ticari_envanter.keys())
            for i, mal in enumerate(envanter_listesi):
                adet = oyuncu.ticari_envanter[mal]
                piyasa_fiyati = piyasa.ticari_mallar[mal]['fiyat']
                uygulanacak_fiyat = int(piyasa_fiyati * sosyal_beceri_bonusu)
                print(f"{i+1}: {mal.capitalize()} ({adet} adet) - Satış Fiyatı: {uygulanacak_fiyat} TL (Piyasa: {piyasa_fiyati} TL)")

            try:
                mal_secim = int(input(f"Ne satmak istersin? (1-{len(envanter_listesi)}): "))
                adet_satis = int(input("Kaç adet satmak istersin?: "))

                secilen_mal_adi = envanter_listesi[mal_secim - 1]

                if adet_satis <= oyuncu.ticari_envanter[secilen_mal_adi]:
                    fiyat = int(piyasa.ticari_mallar[secilen_mal_adi]['fiyat'] * sosyal_beceri_bonusu)
                    toplam_kazanc = fiyat * adet_satis
                    oyuncu.para += toplam_kazanc
                    oyuncu.ticari_envanter[secilen_mal_adi] -= adet_satis
                    if oyuncu.ticari_envanter[secilen_mal_adi] == 0:
                        del oyuncu.ticari_envanter[secilen_mal_adi]
                    piyasa.ticari_mallar[secilen_mal_adi]['arz'] += adet_satis / 10 # Satım arzı artırır
                    print(f"{adet_satis} adet {secilen_mal_adi.capitalize()} sattın ve {toplam_kazanc} TL kazandın.")
                else:
                    print("Elinde o kadar mal yok.")

            except (ValueError, IndexError):
                print("Geçersiz seçim.")

    time.sleep(2)
    return 3 # Ticaret 3 saat sürer


if __name__ == "__main__":
    main()
