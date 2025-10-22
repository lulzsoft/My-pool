# -*- coding: utf-8 -*-

import random
import os
import time

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Veri yapıları ve yardımcı fonksiyonlar
ISIM_LISTESI = ["Ali", "Ayşe", "Mehmet", "Fatma", "Hasan", "Zeynep", "Emre", "Elif"]
SOYISIM_LISTESI = ["Yılmaz", "Kaya", "Demir", "Çelik", "Arslan", "Doğan", "Kurt"]
DEPARTMANLAR = ["Uretim", "Pazarlama", "Tedarik", "Ar-Ge"]

class Calisan:
    def __init__(self, departman, seviye=1):
        self.isim = f"{random.choice(ISIM_LISTESI)} {random.choice(SOYISIM_LISTESI)}"
        self.departman = departman
        self.seviye = seviye
        self.moral = 70
        self.maas = 30 + (seviye * 10) # Seviyeye bağlı maaş

# Ev ve Emlak Sistemi Veri Yapıları
EV_EKSİKLİKLERİ = {
    "Sızdıran Çatı": {"maliyet": 1500, "kategori": "genel"},
    "Bozuk Parke": {"maliyet": 800, "kategori": "oda"},
    "Eski Tesisat": {"maliyet": 2500, "kategori": "genel"},
    "Çatlak Duvarlar": {"maliyet": 600, "kategori": "oda"},
    "Bozuk Prizler": {"maliyet": 300, "kategori": "oda"},
    "Eski Mutfak Dolapları": {"maliyet": 1200, "kategori": "mutfak"},
    "Bozuk Musluklar": {"maliyet": 250, "kategori": "mutfak_banyo"},
    "Tıkalı Giderler": {"maliyet": 400, "kategori": "mutfak_banyo"},
    "Kırık Pencereler": {"maliyet": 700, "kategori": "genel"},
    "Boya İhtiyacı": {"maliyet": 900, "kategori": "genel"},
    "Zayıf İnternet Altyapısı": {"maliyet": 1000, "kategori": "genel"},
    "Yetersiz Isı Yalıtımı": {"maliyet": 1800, "kategori": "genel"},
    "Eski Banyo Fayansları": {"maliyet": 1100, "kategori": "banyo"},
    "Bozuk Kombi/Isıtma Sistemi": {"maliyet": 3000, "kategori": "genel"},
    "Güvenlik Sistemi Eksikliği": {"maliyet": 1300, "kategori": "genel"},
    "Bahçe Bakımsızlığı": {"maliyet": 500, "kategori": "bahce"},
    "Bozuk Bahçe Çiti": {"maliyet": 650, "kategori": "bahce"},
    "Havuz Bakım Sorunu": {"maliyet": 2200, "kategori": "havuz"},
    "Garaj Kapısı Arızası": {"maliyet": 950, "kategori": "garaj"},
    "Küf Sorunu": {"maliyet": 1600, "kategori": "genel"},
    "Haşere Sorunu": {"maliyet": 750, "kategori": "genel"}
}

EV_TİPLERİ = {
    "1+0 Stüdyo Daire": {"min_m2": 35, "max_m2": 50, "temel_fiyat": 60000, "kategoriler": ["genel", "oda", "mutfak_banyo", "banyo"]},
    "1+1 Apartman Dairesi": {"min_m2": 55, "max_m2": 75, "temel_fiyat": 90000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo"]},
    "2+1 Apartman Dairesi": {"min_m2": 80, "max_m2": 110, "temel_fiyat": 150000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo"]},
    "Bahçeli Müstakil Ev": {"min_m2": 120, "max_m2": 200, "temel_fiyat": 250000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo", "bahce", "garaj"]},
    "Villa": {"min_m2": 250, "max_m2": 400, "temel_fiyat": 500000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo", "bahce", "garaj", "havuz"]}
}

class Ev:
    def __init__(self, ev_tipi_adi, metrekare, eksiklikler):
        self.tip = ev_tipi_adi
        self.metrekare = metrekare
        self.eksiklikler = {eksik: False for eksik in eksiklikler} # False: tamir edilmemiş

        temel_bilgi = EV_TİPLERİ[ev_tipi_adi]
        self.satis_fiyati = int(temel_bilgi["temel_fiyat"] + (metrekare * 300))
        self.alis_fiyati = self.satis_fiyati
        for eksik in eksiklikler:
            self.alis_fiyati -= EV_EKSİKLİKLERİ[eksik]["maliyet"]
        self.alis_fiyati = max(10000, int(self.alis_fiyati * random.uniform(0.85, 1.05)))

    def __str__(self):
        tamir_durumu = "Tamir Edilmemiş" if False in self.eksiklikler.values() else "Tamamen Tamir Edilmiş"
        return f"{self.tip} ({self.metrekare} m²) - Durum: {tamir_durumu}"


# Ürün reçeteleri
URUN_RECETELERI = {
    "elektronik cihaz": {"metal": 2, "silikon": 3, "plastik": 1},
    "kıyafet": {"tekstil": 5, "plastik": 1}
}

class Isletme:
    def __init__(self, isim, sermaye, urun_tipi):
        self.isim = isim
        self.sermaye = sermaye
        self.urun_tipi = urun_tipi
        self.departmanlar = {dep: [] for dep in DEPARTMANLAR}
        self.departmanlar["Uretim"].append(Calisan("Uretim", seviye=2)) # Kurucu
        self.musteri_memnuniyeti = 70
        self.hammadde_envanteri = {"metal": 0, "plastik": 0, "silikon": 0, "tekstil": 0}
        self.urun_envanteri = 0
        self.min_stok_seviyesi = 10 # Tedarik departmanı için
        self.ar_ge_seviyesi = 1

    @property
    def calisan_sayisi(self):
        return sum(len(calisan_listesi) for calisan_listesi in self.departmanlar.values())

    def get_ortalama_seviye(self, departman):
        calisan_listesi = self.departmanlar.get(departman, [])
        if not calisan_listesi:
            return 0
        return sum(c.seviye for c in calisan_listesi) / len(calisan_listesi)

    def tedarik_yap(self, piyasa):
        """Tedarik departmanı, eksik hammaddeleri otomatik olarak satın alır."""
        tedarik_seviyesi = self.get_ortalama_seviye("Tedarik")
        indirim_orani = 1 - (tedarik_seviyesi / 100)

        for hammadde, miktar in self.hammadde_envanteri.items():
            if miktar < self.min_stok_seviyesi:
                ihtiyac = self.min_stok_seviyesi - miktar
                if hammadde in piyasa.ticari_mallar:
                    fiyat = piyasa.ticari_mallar[hammadde]["fiyat"] * indirim_orani
                    toplam_tutar = int(ihtiyac * fiyat)

                    if self.sermaye >= toplam_tutar:
                        self.sermaye -= toplam_tutar
                        self.hammadde_envanteri[hammadde] += ihtiyac
                        print(f"\nTedarik dep. {ihtiyac} adet {hammadde} satın aldı (Tutar: {toplam_tutar} TL).")
                    else:
                        print(f"\nTedarik dep. {hammadde} alamadı (Yetersiz sermaye).")

    def uretim_yap(self):
        """Üretim departmanı, hammaddeleri kullanarak ürün üretir."""
        uretim_seviyesi = self.get_ortalama_seviye("Uretim")
        # Ar-Ge seviyesi verimliliğe bonus olarak eklenir. Her Ar-Ge seviyesi %2 verimlilik artışı sağlar.
        verimlilik_bonusu = 1 + (uretim_seviyesi / 100) + (self.ar_ge_seviyesi / 50)

        recete = URUN_RECETELERI.get(self.urun_tipi)
        if not recete: return

        uretilebilecek_max_miktar = float('inf')
        for hammadde, gereken in recete.items():
            gereken_miktar = gereken / verimlilik_bonusu
            if self.hammadde_envanteri.get(hammadde, 0) < gereken_miktar:
                uretilebilecek_max_miktar = 0
                break
            if gereken_miktar > 0:
                uretilebilecek_max_miktar = min(uretilebilecek_max_miktar, self.hammadde_envanteri[hammadde] // gereken_miktar)

        uretilecek_miktar = int(uretilebilecek_max_miktar)
        if uretilecek_miktar > 0:
            for hammadde, gereken in recete.items():
                self.hammadde_envanteri[hammadde] -= int(gereken * uretilecek_miktar / verimlilik_bonusu)
            self.urun_envanteri += uretilecek_miktar
            print(f"Üretim dep. {uretilecek_miktar} adet {self.urun_tipi} üretti.")

    def pazarlama_yap(self, piyasa):
        """Pazarlama departmanı, üretilen ürünleri satar ve net karı döndürür."""
        pazarlama_seviyesi = self.get_ortalama_seviye("Pazarlama")
        fiyat_artisi_orani = 1 + (pazarlama_seviyesi / 100)

        gelir = 0
        satilabilecek_miktar = int(self.urun_envanteri * (self.musteri_memnuniyeti / 100))
        if satilabilecek_miktar > 0:
            urun_fiyati = piyasa.ticari_mallar[self.urun_tipi]["fiyat"] * fiyat_artisi_orani
            gelir = int(satilabilecek_miktar * urun_fiyati)
            self.urun_envanteri -= satilabilecek_miktar
            self.sermaye += gelir
            print(f"Pazarlama dep. {satilabilecek_miktar} adet ürün sattı (Gelir: {gelir} TL).")

        # Giderler (sabit ve maaşlar)
        toplam_maas = sum(c.maas for dep in self.departmanlar.values() for c in dep)
        gider = 50 + toplam_maas
        self.sermaye -= gider

        net_kar = gelir - gider
        return net_kar

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
            "elektronik cihaz": {"fiyat": 1350, "arz": 100, "talep": 110},
            "kıyafet": {"fiyat": 480, "arz": 300, "talep": 320},
            "metal": {"fiyat": 150, "arz": 500, "talep": 500},
            "plastik": {"fiyat": 40, "arz": 1000, "talep": 1000},
            "silikon": {"fiyat": 250, "arz": 300, "talep": 300},
            "tekstil": {"fiyat": 60, "arz": 800, "talep": 800}
        }
        self.fiyat_gecmisi = {mal: [] for mal in self.ticari_mallar}

    def gunluk_guncelle(self, gun):
        """Piyasadaki tüm varlıkların fiyatlarını günceller ve geçmişi kaydeder."""
        # Yatırım mallarını güncelle
        for varlik, detaylar in self.yatirim_mallari.items():
            degisim_yuzdesi = detaylar["trend"] + (random.uniform(-detaylar.get("volatilite", 0.1), detaylar.get("volatilite", 0.1)))
            yeni_fiyat = detaylar["fiyat"] * (1 + degisim_yuzdesi)
            self.yatirim_mallari[varlik]["fiyat"] = max(1, int(yeni_fiyat))

        # Ticari malları güncelle ve geçmişi kaydet
        for mal, detaylar in self.ticari_mallar.items():
            # Fiyat geçmişini kaydet
            self.fiyat_gecmisi[mal].append({"gun": gun, "fiyat": detaylar["fiyat"]})
            if len(self.fiyat_gecmisi[mal]) > 30:
                self.fiyat_gecmisi[mal].pop(0) # En eski kaydı sil

            # Arz ve talebi dalgalandır
            detaylar["arz"] = max(10, detaylar["arz"] + random.randint(-10, 10))
            detaylar["talep"] = max(10, detaylar["talep"] + random.randint(-5, 5))

            # Fiyatı arz-talep dengesine göre ayarla
            fiyat_degisim_orani = (detaylar["talep"] - detaylar["arz"]) / 1000
            yeni_fiyat = detaylar["fiyat"] * (1 + fiyat_degisim_orani)
            self.ticari_mallar[mal]["fiyat"] = max(5, int(yeni_fiyat))

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
        self.gazeteler = [] # Satın alınan gazeteleri saklar
        self.otomasyon_modu = False
        self.universite_gun_sayaci = 0
        self.diploma = False
        self.sahip_olunan_evler = []

magaza_esyalari = {
    "gazete": {"fiyat": 25},
    "kitap": {"fiyat": 75, "etki": "zeka", "deger": 5},
    "konsol oyunu": {"fiyat": 200, "etki": "mutluluk", "deger": 15},
    "abur cubur": {"fiyat": 15, "etki": "aclik", "deger": -40, "metabolizma_etkisi": 0.2},
    "ev yemeği": {"fiyat": 40, "etki": "aclik", "deger": -50, "metabolizma_etkisi": 0},
    "lüks restoran yemeği": {"fiyat": 150, "etki": "aclik", "deger": -70, "metabolizma_etkisi": -0.1},
    "sabun": {"fiyat": 10, "etki": "hijyen", "deger": 20}
}

# Global Emlak İlanları
emlak_ilanlari = []

def emlak_ilanlarini_guncelle():
    """Her 3 günde bir emlak ilanlarını rastgele evlerle yeniler."""
    global emlak_ilanlari
    emlak_ilanlari.clear()

    for _ in range(random.randint(3, 5)): # 3 ila 5 arası yeni ilan
        tip_adi, tip_ozellikleri = random.choice(list(EV_TİPLERİ.items()))
        metrekare = random.randint(tip_ozellikleri["min_m2"], tip_ozellikleri["max_m2"])

        olasi_eksiklikler = [k for k, v in EV_EKSİKLİKLERİ.items() if v["kategori"] in tip_ozellikleri["kategoriler"]]
        eksiklik_sayisi = random.randint(0, min(5, len(olasi_eksiklikler)))
        secilen_eksiklikler = random.sample(olasi_eksiklikler, eksiklik_sayisi)

        yeni_ev = Ev(tip_adi, metrekare, secilen_eksiklikler)
        emlak_ilanlari.append(yeni_ev)
    print("\n--- Emlak Piyasası Güncellendi! Yeni Evler Satışta! ---")
    time.sleep(1)


def main():
    """Ana oyun fonksiyonu."""
    clear_screen()
    isim = input("Karakterinizin ismini girin: ")
    oyuncu = Oyuncu(isim)
    emlak_ilanlarini_guncelle() # Oyuna başlarken ilk ilanlar oluşturulur

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

        if oyuncu.otomasyon_modu:
            yanit = input("Otomasyon devrede... Devam etmek için Enter'a basın veya 'kapat' yazarak modu durdurun: ")
            if yanit.lower() == 'kapat':
                oyuncu.otomasyon_modu = False
                print("Otomasyon modu kapatıldı.")
                time.sleep(2)
                continue
            harcanan_saat = otomasyonu_calistir(oyuncu, zaman, piyasa)
        else:
            harcanan_saat = eylem_sec(oyuncu, zaman, piyasa)

        # Zamanı ilerlet
        for _ in range(harcanan_saat):
            zaman.saat += 1
            saati_ilerlet(oyuncu, zaman, zaman.saat)
            if zaman.saat >= 24:
                zaman.saat = 0
                zaman.gun += 1
                piyasa.gunluk_guncelle(zaman.gun)
                if oyuncu.isletme:
                    oyuncu.isletme.tedarik_yap(piyasa)
                    oyuncu.isletme.uretim_yap()
                    net_kar = oyuncu.isletme.pazarlama_yap(piyasa)
                    oyuncu.para += net_kar
                    print(f"\nİşletmen bugün {net_kar} TL {'kar' if net_kar >= 0 else 'zarar'} etti.")
                    time.sleep(1)
                # Yaşlanma kontrolü
                if zaman.gun % 365 == 0:
                    oyuncu.yas += 1
                    print(f"\nDoğum günün kutlu olsun! Artık {oyuncu.yas} yaşındasın.")
                    time.sleep(2)

        if oyuncu.saglik <= 0:
            oyun_bitti = True
            print("\nSağlığın tükendi ve hayatını kaybettin. Oyun bitti.")

def saati_ilerlet(oyuncu, zaman, saat):
    """Zamanı bir saat ilerletir ve statları günceller."""
    # Günlük güncellemeler (her gece yarısı tetiklenir)
    if saat == 0:
        # Üniversite ilerlemesi
        if oyuncu.universite_gun_sayaci > 0:
            oyuncu.universite_gun_sayaci = max(0, oyuncu.universite_gun_sayaci - 1)
            if oyuncu.universite_gun_sayaci == 0 and not oyuncu.diploma:
                oyuncu.diploma = True
                print("\nTEBRİKLER! Üniversiteyi bitirdin ve diplomanı aldın!")

        # Emlak ilanlarını yenileme
        if zaman.gun % 3 == 0:
            emlak_ilanlarini_guncelle()

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

def bar_gostergesi_olustur(label, deger, max_deger=100, uzunluk=10):
    """Metin tabanlı bir ilerleme çubuğu oluşturur."""
    oran = deger / max_deger
    dolu_uzunluk = int(oran * uzunluk)
    bos_uzunluk = uzunluk - dolu_uzunluk
    bar = "█" * dolu_uzunluk + "-" * bos_uzunluk
    return f"{label:<10}: [{bar}] {int(deger)}%"

def durumu_goster(oyuncu, zaman, piyasa):
    """Oyuncunun anlık durumunu gösterir."""
    clear_screen()
    print(f"--- {zaman} ---")
    print("--- GÜNCEL DURUM ---")
    print(f"İsim: {oyuncu.isim}  |  Yaş: {oyuncu.yas}  |  Diploma: {'Var' if oyuncu.diploma else 'Yok'}")
    print("-" * 20)
    print(bar_gostergesi_olustur("Sağlık", oyuncu.saglik))
    print(bar_gostergesi_olustur("Mutluluk", oyuncu.mutluluk))
    print(bar_gostergesi_olustur("Enerji", oyuncu.enerji))
    print(bar_gostergesi_olustur("Açlık", oyuncu.aclik))
    print(bar_gostergesi_olustur("Hijyen", oyuncu.hijyen))
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

    if oyuncu.sahip_olunan_evler:
        print("-" * 20)
        print("Sahip Olduğun Evler:")
        for ev in oyuncu.sahip_olunan_evler:
            print(f" - {ev}")

    print("--------------------")

def emlakciya_git(oyuncu):
    """Emlakçıya giderek ev alım satım ve yönetim işlemlerini yapar."""
    print("\n--- EMLAKÇI ---")
    print("1: Satılık İlanları Görüntüle")
    print("2: Sahip Olduğun Evleri Yönet")
    print("3: Ev Sat")

    secim = input("Ne yapmak istersin? (1-3), çıkmak için 0): ")

    if secim == '1':
        if not emlak_ilanlari:
            print("Şu anda hiç satılık ev ilanı yok.")
        else:
            print("\n--- SATILIK EV İLANLARI ---")
            for i, ev in enumerate(emlak_ilanlari):
                print(f"{i+1}: {ev.tip} ({ev.metrekare} m²) - Fiyat: {ev.alis_fiyati} TL")

            try:
                secim_ev = int(input(f"Satın almak istediğin evin numarasını gir (1-{len(emlak_ilanlari)}), çıkmak için 0): "))
                if secim_ev > 0:
                    secilen_ev = emlak_ilanlari[secim_ev - 1]
                    if oyuncu.para >= secilen_ev.alis_fiyati:
                        oyuncu.para -= secilen_ev.alis_fiyati
                        oyuncu.sahip_olunan_evler.append(secilen_ev)
                        emlak_ilanlari.pop(secim_ev - 1)
                        print(f"Tebrikler! {secilen_ev.tip} satın aldın.")
                    else:
                        print("Bu evi almak için yeterli paran yok.")
            except (ValueError, IndexError):
                print("Geçersiz seçim.")

    elif secim == '2':
        if not oyuncu.sahip_olunan_evler:
            print("Yönetilecek hiç evin yok.")
        else:
            print("\n--- EVLERİNİ YÖNET ---")
            for i, ev in enumerate(oyuncu.sahip_olunan_evler):
                print(f"{i+1}: {ev}")

            try:
                secim_yonet = int(input(f"Yönetmek istediğin evin numarasını gir (1-{len(oyuncu.sahip_olunan_evler)}): "))
                if secim_yonet > 0:
                    secilen_ev = oyuncu.sahip_olunan_evler[secim_yonet - 1]
                    print(f"\n--- {secilen_ev.tip} Yönetimi ---")
                    print("Eksiklikler:")
                    tamir_edilecekler = []
                    for eksik, durum in secilen_ev.eksiklikler.items():
                        durum_str = "Tamir Edilmiş" if durum else "Tamir Bekliyor"
                        maliyet = EV_EKSİKLİKLERİ[eksik]["maliyet"]
                        print(f" - {eksik}: {durum_str} (Maliyet: {maliyet} TL)")
                        if not durum:
                            tamir_edilecekler.append(eksik)

                    if not tamir_edilecekler:
                        print("Bu evde tamir edilecek bir şey yok.")
                    else:
                        onay = input("Bu evdeki tüm eksiklikleri tamir ettirmek istiyor musun? (e/h): ").lower()
                        if onay == 'e':
                            toplam_maliyet = sum(EV_EKSİKLİKLERİ[e]["maliyet"] for e in tamir_edilecekler)
                            print(f"Toplam tamir maliyeti: {toplam_maliyet} TL.")
                            if oyuncu.para >= toplam_maliyet:
                                oyuncu.para -= toplam_maliyet
                                for eksik in tamir_edilecekler:
                                    secilen_ev.eksiklikler[eksik] = True
                                print("Usta çağrıldı ve tüm eksiklikler giderildi!")
                            else:
                                print("Tamir için yeterli paran yok.")
            except (ValueError, IndexError):
                print("Geçersiz seçim.")

    elif secim == '3':
        if not oyuncu.sahip_olunan_evler:
            print("Satacak hiç evin yok.")
        else:
            print("\n--- EV SAT ---")
            for i, ev in enumerate(oyuncu.sahip_olunan_evler):
                print(f"{i+1}: {ev} - Potansiyel Satış Fiyatı: {ev.satis_fiyati} TL")

            try:
                secim_sat = int(input(f"Satmak istediğin evin numarasını gir (1-{len(oyuncu.sahip_olunan_evler)}): "))
                if secim_sat > 0:
                    satilacak_ev = oyuncu.sahip_olunan_evler[secim_sat - 1]
                    if False in satilacak_ev.eksiklikler.values():
                        print("Bu evi satamazsın! Önce tüm eksiklikleri tamir etmelisin.")
                    else:
                        oyuncu.para += satilacak_ev.satis_fiyati
                        oyuncu.sahip_olunan_evler.pop(secim_sat - 1)
                        print(f"{satilacak_ev.tip} satıldı ve {satilacak_ev.satis_fiyati} TL kazandın!")
            except (ValueError, IndexError):
                print("Geçersiz seçim.")

    input("\nDevam etmek için Enter'a bas...")
    return 2


def eylem_sec(oyuncu, zaman, piyasa):
    """Oyuncunun eylem seçmesini sağlar ve sonucu uygular."""
    print("\nNe yapmak istersin?")
    print("1: Çalış")
    print("2: Uyu")
    print("3: Eğlen")
    print("4: Eğitim Al (Okul/Üniversite)")
    print("5: Spor Yap")
    print("6: Alışveriş Yap")
    print("7: Kitap Oku")
    print("8: Envanteri Kullan")
    print("9: Yatırım Yap")
    print("10: İş Kur / Yönet")
    print("11: Ticaret Yap")
    print("12: Gazete Oku")
    print("13: Emlakçıya Git")
    print("14: Otomasyon Modunu Değiştir")

    secim = input("Seçimin (1-14): ")

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
        return alisveris_yap(oyuncu, zaman, piyasa)
    elif secim == '7':
        return kitap_oku(oyuncu)
    elif secim == '8':
        return envanter_kullan(oyuncu)
    elif secim == '9':
        return yatirim_yap(oyuncu, piyasa)
    elif secim == '10':
        return is_kur(oyuncu) if oyuncu.isletme is None else isletmeyi_yonet(oyuncu, piyasa)
    elif secim == '11':
        return ticaret_yap(oyuncu, piyasa)
    elif secim == '12':
        return gazete_oku(oyuncu)
    elif secim == '13':
        return emlakciya_git(oyuncu)
    elif secim == '14':
        oyuncu.otomasyon_modu = not oyuncu.otomasyon_modu
        print(f"Otomasyon modu şimdi {'AÇIK' if oyuncu.otomasyon_modu else 'KAPALI'}.")
        time.sleep(2)
        return 1
    else:
        print("Geçersiz seçim. 1 saatin boşa geçti.")
        time.sleep(1)
        return 1

def otomasyonu_calistir(oyuncu, zaman, piyasa):
    """Otomasyon modu aktifken oyuncunun temel ihtiyaçlarını karşılar."""
    print("\n--- OTOMASYON DEVREDE ---")

    # Yüksek öncelikli acil durumlar
    if oyuncu.aclik > 80:
        print("Otomasyon: Açlık kritik seviyede, yemek yeniyor.")
        yemekler = [y for y in oyuncu.envanter if "yemeği" in y or "abur cubur" in y]
        if yemekler:
            return envanter_kullan(oyuncu, override_secim=yemekler[0])
        else:
            print("Otomasyon: Yiyecek kalmamış, markete gidiliyor.")
            return alisveris_yap(oyuncu, zaman, piyasa, otomasyon_hedef="ev yemeği")

    if oyuncu.hijyen < 20:
        print("Otomasyon: Hijyen düşük, duş alınıyor.")
        if "sabun" in oyuncu.envanter:
            return envanter_kullan(oyuncu, override_secim="sabun")
        else:
            return alisveris_yap(oyuncu, zaman, piyasa, otomasyon_hedef="sabun")

    # Enerji yönetimi ve çalışma
    if oyuncu.enerji < 40:
        print("Otomasyon: Enerji çalışmak için yetersiz, uyumak gerekiyor.")
        return uyu(oyuncu)
    else:
        # Temel ihtiyaçlar karşılandıysa ve enerji yeterliyse para kazan
        print("Otomasyon: Temel ihtiyaçlar yerinde ve enerji yeterli, çalışmaya gidiliyor.")
        return calis(oyuncu)


def alisveris_yap(oyuncu, zaman, piyasa, otomasyon_hedef=None):
    """Alışveriş yapma eylemi."""
    if otomasyon_hedef:
        secilen_esya_adi = otomasyon_hedef
    else:
        print("\n--- MAĞAZA ---")
        for i, (esya, detaylar) in enumerate(magaza_esyalari.items()):
            print(f"{i+1}: {esya.capitalize()} - {detaylar['fiyat']} TL")

        try:
            secim = int(input(f"Ne almak istersin? (1-{len(magaza_esyalari)}), çıkmak için 0): "))
            if secim == 0:
                return 1

            secilen_esya_adi = list(magaza_esyalari.keys())[secim - 1]
        except (ValueError, IndexError):
            print("Geçersiz seçim.")
            time.sleep(2)
            return 1

    if secilen_esya_adi in magaza_esyalari:
        secilen_esya = magaza_esyalari[secilen_esya_adi]

        if oyuncu.para >= secilen_esya['fiyat']:
            oyuncu.para -= secilen_esya['fiyat']
            if secilen_esya_adi == "gazete":
                import copy
                yeni_gazete = {"gun": zaman.gun, "fiyat_gecmisi": copy.deepcopy(piyasa.fiyat_gecmisi)}
                oyuncu.gazeteler.append(yeni_gazete)
                print(f"Gün {zaman.gun} tarihli gazete satın aldın.")
            else:
                oyuncu.envanter.append(secilen_esya_adi)
                print(f"{secilen_esya_adi.capitalize()} satın aldın.")
        else:
            print("Yeterli paran yok.")
    time.sleep(2)
    return 1

def kitap_oku(oyuncu):
    """Kitap okuma eylemi."""
    if "kitap" in oyuncu.envanter:
        print("1 saat kitap okuyarak zekanı geliştirdin.")
        oyuncu.zeka = min(100, oyuncu.zeka + magaza_esyalari["kitap"]["deger"])
        oyuncu.enerji -= 5
        oyuncu.mutluluk += 5
        oyuncu.envanter.remove("kitap")
        time.sleep(2)
        return 1
    else:
        print("Okuyacak bir kitabın yok. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

def envanter_kullan(oyuncu, override_secim=None):
    """Envanterdeki bir eşyayı kullanma eylemi."""
    if not oyuncu.envanter:
        print("Envanterin boş. 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

    if override_secim:
        secilen_esya_adi = override_secim
    else:
        print("\n--- ENVANTER ---")
        for i, esya in enumerate(oyuncu.envanter):
            print(f"{i+1}: {esya.capitalize()}")

        try:
            secim = int(input(f"Ne kullanmak istersin? (1-{len(oyuncu.envanter)}), çıkmak için 0): "))
            if secim == 0:
                return 1

            secilen_esya_adi = oyuncu.envanter[secim - 1]
        except (ValueError, IndexError):
            print("Geçersiz seçim.")
            time.sleep(2)
            return 1

    if secilen_esya_adi in oyuncu.envanter:
        esya_detay = magaza_esyalari[secilen_esya_adi]
        etki_alani = esya_detay.get('etki')
        if not etki_alani:
            print("Bu eşyanın bir etkisi yok.")
            time.sleep(2)
            return 1

        deger = esya_detay['deger']
        mevcut_deger = getattr(oyuncu, etki_alani)
        setattr(oyuncu, etki_alani, min(100, max(0, mevcut_deger + deger)))

        if "metabolizma_etkisi" in esya_detay:
            oyuncu.metabolizma_hizi = 1.0 + esya_detay["metabolizma_etkisi"]
            oyuncu.metabolizma_etki_suresi = 4
            print(f"Yediğin yiyecek metabolizmanı etkiledi! Mevcut hız: {oyuncu.metabolizma_hizi}x")

        print(f"{secilen_esya_adi.capitalize()} kullandın. {etki_alani.capitalize()} {deger} değişti.")
        oyuncu.envanter.remove(secilen_esya_adi)

    time.sleep(2)
    return 1

def calis(oyuncu):
    """Çalışma eylemi."""
    if oyuncu.isletme:
        print("Kendi işinin patronusun, 'İşletmeyi Yönet' seçeneğini kullan.")
        time.sleep(2)
        return 1
    if oyuncu.enerji >= 40:
        saat = 8
        kazanc_per_saat = 10 + (oyuncu.zeka // 10) + (oyuncu.is_emegi // 10)
        if oyuncu.diploma:
            print("Üniversite diploman sayesinde daha kazançlı bir iş buldun!")
            kazanc_per_saat *= 3
        toplam_kazanc = kazanc_per_saat * saat
        print(f"{saat} saat çalıştın ve {toplam_kazanc} TL kazandın.")
        oyuncu.para += toplam_kazanc
        oyuncu.enerji -= 40
        oyuncu.mutluluk -= 15
        oyuncu.is_emegi += saat

        if oyuncu.is_emegi >= 200:
            print("\nTebrikler! Terfi aldın! Saatlik ücretin arttı.")

        time.sleep(2)
        return saat
    else:
        print("Çok yorgunsun, tam gün çalışamazsın. Sadece 1 saatin boşa geçti.")
        time.sleep(2)
        return 1

def uyu(oyuncu):
    """Uyuma eylemi."""
    if oyuncu.otomasyon_modu:
        saat = 8
    else:
        try:
            saat_str = input("Kaç saat uyumak istersin? (1-10): ")
            saat = int(saat_str) if saat_str else 8
        except ValueError:
            saat = 8

    saat = max(1, min(10, saat))
    print(f"{saat} saat uyudun.")
    oyuncu.enerji = min(100, oyuncu.enerji + saat * 8)
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
    """Okula gitme ve üniversite eğitimi alma eylemi."""
    UNIVERSITE_SURESI = 1460 # 4 oyun yılı
    ZEKA_GEREKSINIMI = 80

    if oyuncu.diploma:
        print("Zaten bir üniversite diploman var!")
        time.sleep(2)
        return 1

    if oyuncu.universite_gun_sayaci > 0:
        if oyuncu.enerji >= 30 and oyuncu.para >= 100:
            gun_ilerlemesi = 5
            print(f"Üniversiteye gidip {gun_ilerlemesi} gün boyunca ders çalıştın.")
            oyuncu.universite_gun_sayaci = max(0, oyuncu.universite_gun_sayaci - gun_ilerlemesi)
            oyuncu.enerji -= 30
            oyuncu.para -= 100
            oyuncu.mutluluk -= 15

            if oyuncu.universite_gun_sayaci == 0:
                oyuncu.diploma = True
                print("\nTEBRİKLER! Üniversiteden başarıyla mezun oldun ve bir diploma kazandın!")
            else:
                print(f"Mezuniyete kalan süre: {oyuncu.universite_gun_sayaci} gün.")

            time.sleep(2)
            return 8 # Üniversite günü 8 saat sürer
        else:
            print("Üniversiteye gidecek enerjin veya paran yok. 1 saatin boşa geçti.")
            time.sleep(2)
            return 1

    else: # Henüz üniversiteye başlamamış
        print("\n--- EĞİTİM SEÇENEKLERİ ---")
        print("1: Okula Git (Zeka artırır)")
        if oyuncu.zeka >= ZEKA_GEREKSINIMI:
            print(f"2: Üniversiteye Başla (Gereksinim: {ZEKA_GEREKSINIMI} Zeka)")

        secim = input("Seçimin: ")
        if secim == '1':
            if oyuncu.enerji >= 20 and oyuncu.para >= 50:
                print("Okula gidip 4 saat ders çalıştın.")
                oyuncu.zeka = min(100, oyuncu.zeka + 5)
                oyuncu.enerji -= 20
                oyuncu.para -= 50
                oyuncu.mutluluk -= 10
                time.sleep(2)
                return 4
            else:
                print("Okula gidecek enerjin veya paran yok. 1 saatin boşa geçti.")
                time.sleep(2)
                return 1
        elif secim == '2' and oyuncu.zeka >= ZEKA_GEREKSINIMI:
            print(f"Üniversiteye kaydoldun! {UNIVERSITE_SURESI} gün sürecek zorlu bir macera başlıyor.")
            oyuncu.universite_gun_sayaci = UNIVERSITE_SURESI
            time.sleep(3)
            return 2
        else:
            print("Geçersiz seçim. 1 saatin boşa geçti.")
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
    return 2

def is_kur(oyuncu):
    """Yeni bir iş kurma eylemi."""
    kurulum_maliyeti = 2500
    print(f"\nKendi işini kurmak için gereken başlangıç sermayesi {kurulum_maliyeti} TL.")
    print("Hangi alanda bir iş kurmak istersin?")
    urun_tipleri = list(URUN_RECETELERI.keys())
    for i, urun in enumerate(urun_tipleri):
        print(f"{i+1}: {urun.capitalize()} Üretimi")

    try:
        secim = int(input(f"Seçimin (1-{len(urun_tipleri)}): "))
        urun_tipi = urun_tipleri[secim - 1]

        if oyuncu.para >= kurulum_maliyeti:
            isletme_ismi = input("İşletmenin adı ne olsun?: ")
            oyuncu.para -= kurulum_maliyeti
            oyuncu.isletme = Isletme(isletme_ismi, kurulum_maliyeti, urun_tipi)
            print(f"Tebrikler! '{isletme_ismi}' adında bir {urun_tipi} şirketi kurdun.")
        else:
            print("Yeterli paran yok.")
    except (ValueError, IndexError):
        print("Geçersiz seçim.")
    time.sleep(2)
    return 3

def isletmeyi_yonet(oyuncu, piyasa):
    """Mevcut işletmeyi yönetme eylemi."""
    isletme = oyuncu.isletme
    print(f"\n--- {isletme.isim.upper()} YÖNETİM PANELİ ---")
    print(f"Sermaye: {isletme.sermaye} TL | Çalışanlar: {isletme.calisan_sayisi} | Müşteri Memnuniyeti: {isletme.musteri_memnuniyeti}% | Ar-Ge Seviyesi: {isletme.ar_ge_seviyesi}")
    hammadde_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in isletme.hammadde_envanteri.items() if v > 0])
    print(f"Hammadde Envanteri: {hammadde_str if hammadde_str else 'Boş'}")
    print(f"Ürün Envanteri: {isletme.urun_envanteri} adet {isletme.urun_tipi}")
    print("-" * 20)
    print("--- İNSAN KAYNAKLARI ---")
    print("1: Çalışanları Listele")
    print("2: Çalışan İşe Al")
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
        for dep, calisan_listesi in isletme.departmanlar.items():
            if calisan_listesi:
                print(f"\n-- {dep} Departmanı (Ort. Seviye: {isletme.get_ortalama_seviye(dep):.2f}) --")
                for calisan in calisan_listesi:
                    print(f"  - {calisan.isim} (Seviye: {calisan.seviye}, Maaş: {calisan.maas}, Moral: {calisan.moral})")

    elif secim == '2':
        print("Hangi departmana alım yapmak istersin?")
        for i, dep in enumerate(DEPARTMANLAR):
            print(f"{i+1}: {dep}")
        try:
            dep_secim = int(input(f"Seçimin (1-{len(DEPARTMANLAR)}): "))
            adet = int(input("Kaç kişi işe almak istersin?: "))
            departman = DEPARTMANLAR[dep_secim - 1]

            adaylar = [Calisan(departman, seviye=random.randint(1,5)) for _ in range(adet + 2)] # Fazladan aday
            print("\n--- ADAY LİSTESİ ---")
            for i, aday in enumerate(adaylar):
                print(f"{i+1}: {aday.isim} (Seviye: {aday.seviye}, Maaş: {aday.maas})")

            ise_alinacaklar_str = input("İşe almak istediğin adayların numaralarını virgülle ayırarak yaz (örn: 1,3): ")
            if ise_alinacaklar_str:
                for idx_str in ise_alinacaklar_str.split(','):
                    idx = int(idx_str.strip()) - 1
                    if 0 <= idx < len(adaylar):
                        maliyet = 500 + adaylar[idx].maas # İşe alım maliyeti + ilk maaş
                        if isletme.sermaye >= maliyet:
                            isletme.sermaye -= maliyet
                            isletme.departmanlar[departman].append(adaylar[idx])
                            print(f"{adaylar[idx].isim}, {departman} departmanına katıldı.")
                        else:
                            print(f"{adaylar[idx].isim} için yeterli sermaye yok.")
        except (ValueError, IndexError):
            print("Geçersiz seçim.")

    elif secim == '3':
        calisanlar = []
        for dep, calisan_listesi in isletme.departmanlar.items():
            for calisan in calisan_listesi:
                calisanlar.append((dep, calisan))

        if not calisanlar:
            print("Kovacak çalışan yok.")
        else:
            print("\n--- ÇALIŞAN KOV ---")
            for i, (dep, calisan) in enumerate(calisanlar):
                print(f"{i+1}: {calisan.isim} ({dep}) - Seviye: {calisan.seviye}")

            try:
                secim_kov = int(input(f"Kimi kovmak istersin? (1-{len(calisanlar)}), çıkmak için 0): "))
                if secim_kov > 0:
                    dep, calisan_to_fire = calisanlar[secim_kov - 1]
                    isletme.departmanlar[dep].remove(calisan_to_fire)
                    print(f"{calisan_to_fire.isim} işten çıkarıldı.")
            except (ValueError, IndexError):
                print("Geçersiz seçim.")

    elif secim == '4':
        if isletme.sermaye >= 1000:
            isletme.sermaye -= 1000
            for dep in isletme.departmanlar.values():
                for calisan in dep:
                    calisan.seviye += random.randint(1, 2)
            print("Tüm çalışanlara eğitim verildi, seviyeleri arttı.")
        else:
            print("Eğitim için işletmenin yeterli sermayesi yok.")

    elif secim == '5':
        if isletme.sermaye >= 750:
            isletme.sermaye -= 750
            for dep in isletme.departmanlar.values():
                for calisan in dep:
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
        if isletme.sermaye >= 300:
            isletme.sermaye -= 300
            isletme.musteri_memnuniyeti = min(100, isletme.musteri_memnuniyeti + 15)
            print("Pazarlama kampanyası müşteri memnuniyetini artırdı.")
        else:
            print("Pazarlama için işletmenin yeterli sermayesi yok.")

    elif secim == '8':
        print("\n--- HAMMADDE SATIN AL ---")
        hammadde_listesi = list(isletme.hammadde_envanteri.keys())
        for i, hammadde in enumerate(hammadde_listesi):
            fiyat = piyasa.ticari_mallar[hammadde]['fiyat']
            print(f"{i+1}: {hammadde.capitalize()} - {fiyat} TL")

        try:
            secim_h = int(input(f"Ne almak istersin? (1-{len(hammadde_listesi)}): "))
            adet = int(input("Kaç adet almak istersin?: "))

            secilen_hammadde = hammadde_listesi[secim_h - 1]
            fiyat = piyasa.ticari_mallar[secilen_hammadde]['fiyat']
            toplam_tutar = fiyat * adet

            if isletme.sermaye >= toplam_tutar:
                isletme.sermaye -= toplam_tutar
                isletme.hammadde_envanteri[secilen_hammadde] += adet
                print(f"{adet} adet {secilen_hammadde.capitalize()} satın alındı.")
            else:
                print("İşletmenin yeterli sermayesi yok.")
        except (ValueError, IndexError):
            print("Geçersiz seçim.")

    elif secim == '9':
        maliyet = 2000 * isletme.ar_ge_seviyesi
        print(f"Mevcut Ar-Ge Seviyesi: {isletme.ar_ge_seviyesi}. Bir sonraki seviye için yatırım maliyeti: {maliyet} TL.")
        onay = input("Yatırım yapmak istiyor musun? (e/h): ").lower()
        if onay == 'e':
            if isletme.sermaye >= maliyet:
                isletme.sermaye -= maliyet
                isletme.ar_ge_seviyesi += 1
                print(f"Ar-Ge yatırımı yapıldı! Yeni Ar-Ge Seviyesi: {isletme.ar_ge_seviyesi}.")
            else:
                print("Yatırım için işletmenin yeterli sermayesi yok.")

    elif secim == '10':
        satis_degeri = isletme.sermaye # Basit hesaplama
        print(f"İşletmenin tahmini satış değeri: {satis_degeri} TL.")
        onay = input("İşletmeyi bu fiyata satmak istediğine emin misin? (e/h): ").lower()
        if onay == 'e':
            oyuncu.para += satis_degeri
            oyuncu.isletme = None
            print("İşletmeyi başarıyla sattın!")

    time.sleep(2)
    return 4

def ticaret_yap(oyuncu, piyasa):
    """Ticari mal alıp satma eylemi."""
    print("\n--- TİCARET MERKEZİ ---")
    print("1: Mal Al")
    print("2: Mal Sat")
    secim = input("Ne yapmak istersin? (1-2), çıkmak için 0): ")

    if secim == '0':
        return 1 # Eylem iptal edildi, 1 saat harcandı

    if secim == '1':
        print("\n--- PİYASA (ALIM) ---")
        mal_listesi = list(piyasa.ticari_mallar.keys())
        for i, (mal, detaylar) in enumerate(piyasa.ticari_mallar.items()):
            print(f"{i+1}: {mal.capitalize()} - {detaylar['fiyat']} TL")

        try:
            mal_secim_str = input(f"Ne almak istersin? (1-{len(mal_listesi)}): ")
            if not mal_secim_str: return 1
            mal_secim = int(mal_secim_str)

            adet_str = input("Kaç adet almak istersin?: ")
            if not adet_str: return 1
            adet = int(adet_str)

            if adet <= 0:
                print("Geçersiz adet.")
                time.sleep(2)
                return 2

            secilen_mal_adi = mal_listesi[mal_secim - 1]
            fiyat = piyasa.ticari_mallar[secilen_mal_adi]['fiyat']
            toplam_tutar = fiyat * adet

            if oyuncu.para >= toplam_tutar:
                oyuncu.para -= toplam_tutar
                oyuncu.ticari_envanter[secilen_mal_adi] = oyuncu.ticari_envanter.get(secilen_mal_adi, 0) + adet
                print(f"{adet} adet {secilen_mal_adi.capitalize()} satın aldın.")
            else:
                print("Yeterli paran yok.")
        except (ValueError, IndexError):
            print("Geçersiz seçim.")

    elif secim == '2':
        if not oyuncu.ticari_envanter:
            print("Satacak hiçbir ticari malın yok.")
        else:
            print("\n--- TİCARİ ENVANTER (SATIM) ---")
            envanter_listesi = list(oyuncu.ticari_envanter.keys())
            for i, mal in enumerate(envanter_listesi):
                adet = oyuncu.ticari_envanter[mal]
                mevcut_fiyat = piyasa.ticari_mallar[mal]['fiyat']
                print(f"{i+1}: {mal.capitalize()} ({adet} adet) - Mevcut Fiyat: {mevcut_fiyat} TL")

            try:
                mal_secim_str = input(f"Ne satmak istersin? (1-{len(envanter_listesi)}): ")
                if not mal_secim_str: return 1
                mal_secim = int(mal_secim_str)

                adet_satis_str = input("Kaç adet satmak istersin?: ")
                if not adet_satis_str: return 1
                adet_satis = int(adet_satis_str)

                if adet_satis <= 0:
                    print("Geçersiz adet.")
                    time.sleep(2)
                    return 2

                secilen_mal_adi = envanter_listesi[mal_secim - 1]

                if adet_satis <= oyuncu.ticari_envanter.get(secilen_mal_adi, 0):
                    fiyat = piyasa.ticari_mallar[secilen_mal_adi]['fiyat']
                    toplam_kazanc = fiyat * adet_satis
                    oyuncu.para += toplam_kazanc
                    oyuncu.ticari_envanter[secilen_mal_adi] -= adet_satis
                    if oyuncu.ticari_envanter[secilen_mal_adi] == 0:
                        del oyuncu.ticari_envanter[secilen_mal_adi]
                    print(f"{adet_satis} adet {secilen_mal_adi.capitalize()} sattın ve {toplam_kazanc} TL kazandın.")
                else:
                    print("Elinde o kadar mal yok.")
            except (ValueError, IndexError):
                print("Geçersiz seçim.")
    else:
        print("Geçersiz seçim.")

    time.sleep(2)
    return 2

def gazete_oku(oyuncu):
    """Satın alınmış bir gazeteyi okuma eylemi."""
    if not oyuncu.gazeteler:
        print("Okuyacak hiç gazeten yok.")
        time.sleep(2)
        return 1

    print("\n--- GAZETELERİN ---")
    for i, gazete in enumerate(oyuncu.gazeteler):
        print(f"{i+1}: Gün {gazete['gun']} Tarihli Gazete")

    try:
        secim = int(input(f"Hangi gazeteyi okumak istersin? (1-{len(oyuncu.gazeteler)}), çıkmak için 0): "))
        if secim == 0:
            return 1

        secilen_gazete = oyuncu.gazeteler[secim - 1]
        print(f"\n--- GÜN {secilen_gazete['gun']} PİYASA BÜLTENİ ---")
        for mal, gecmis_veriler in secilen_gazete['fiyat_gecmisi'].items():
            print(f"\n--- {mal.capitalize()} ---")
            if not gecmis_veriler:
                print("Veri yok.")
            else:
                for veri in gecmis_veriler:
                    print(f"  Gün {veri['gun']}: {veri['fiyat']} TL")

        oyuncu.gazeteler.pop(secim - 1)
        print("\nGazeteyi okuduktan sonra attın.")

    except (ValueError, IndexError):
        print("Geçersiz seçim.")

    input("\nDevam etmek için Enter'a bas...")
    return 1

if __name__ == "__main__":
    main()
