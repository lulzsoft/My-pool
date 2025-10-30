# -*- coding: utf-8 -*-

import random

# Bu dosya, oyun içindeki tüm temel veri yapılarını (sınıfları) barındırır.
# Örneğin: Oyuncu, Ev, Isletme, Calisan vb.

# Bağımlılıkları azaltmak için sabit verileri (veri.py'den gelecek)
# ve diğer sistemleri (sistemler.py'den gelecek) buraya import ETMEYECEĞİZ.
# Bu sınıflar, bu verileri metod argümanları olarak alacak şekilde tasarlanmalıdır.

class Calisan:
    def __init__(self, isim, departman, seviye=1):
        self.isim = isim
        self.departman = departman
        self.seviye = seviye
        self.moral = 70
        self.maas = 30 + (seviye * 10)

class NPC:
    def __init__(self, isim, iliski_turu):
        self.isim = isim
        self.iliski_turu = iliski_turu
        self.iliski_seviyesi = random.randint(20, 40)

    def __str__(self):
        return f"{self.isim} ({self.iliski_turu}) - İlişki: {self.iliski_seviyesi}/100"

class Konum:
    def __init__(self, ad, mumkun_eylemler):
        self.ad = ad
        self.mumkun_eylemler = mumkun_eylemler

class Kariyer:
    def __init__(self, ad, diploma_gereksinimi, seviyeler):
        self.ad = ad
        self.diploma_gereksinimi = diploma_gereksinimi
        self.seviyeler = seviyeler

    def get_seviye_bilgisi(self, seviye):
        return self.seviyeler.get(seviye)

class Ev:
    def __init__(self, ev_tipi_adi, metrekare, eksiklikler, ev_tipleri_data, ev_eksiklikleri_data):
        self.tip = ev_tipi_adi
        self.metrekare = metrekare
        self.eksiklikler = {eksik: False for eksik in eksiklikler}

        temel_bilgi = ev_tipleri_data[ev_tipi_adi]
        self.satis_fiyati = int(temel_bilgi["temel_fiyat"] + (metrekare * 300))
        self.alis_fiyati = self.satis_fiyati
        for eksik in eksiklikler:
            self.alis_fiyati -= ev_eksiklikleri_data[eksik]["maliyet"]
        self.alis_fiyati = max(10000, int(self.alis_fiyati * random.uniform(0.85, 1.05)))

    def __str__(self):
        tamir_durumu = "Tamir Edilmemiş" if False in self.eksiklikler.values() else "Tamamen Tamir Edilmiş"
        return f"{self.tip} ({self.metrekare} m²) - Durum: {tamir_durumu}"

class Isletme:
    def __init__(self, isim, sermaye, urun_tipi, departmanlar_listesi, urun_receteleri):
        self.isim = isim
        self.sermaye = sermaye
        self.urun_tipi = urun_tipi
        self.departmanlar = {dep: [] for dep in departmanlar_listesi}
        # Kurucuyu temsilen başlangıç çalışanı
        self.departmanlar["Uretim"].append(Calisan("Kurucu", "Uretim", seviye=2))
        self.musteri_memnuniyeti = 70
        self.hammadde_envanteri = {"metal": 0, "plastik": 0, "silikon": 0, "tekstil": 0}
        self.urun_envanteri = 0
        self.min_stok_seviyesi = 10
        self.ar_ge_seviyesi = 1
        self.urun_receteleri = urun_receteleri # Bağımlılığı dışarıdan al

    @property
    def calisan_sayisi(self):
        return sum(len(calisan_listesi) for calisan_listesi in self.departmanlar.values())

    def get_ortalama_seviye(self, departman):
        calisan_listesi = self.departmanlar.get(departman, [])
        if not calisan_listesi:
            return 0
        return sum(c.seviye for c in calisan_listesi) / len(calisan_listesi)

    def tedarik_yap(self, piyasa):
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
                        piyasa.ticari_mallar[hammadde]["talep"] += ihtiyac # PİYASA ETKİSİ
                        print(f"\n[{self.isim}] Tedarik dep. {ihtiyac} adet {hammadde} satın aldı (Tutar: {toplam_tutar} TL).")
                    # Sermaye yetersizse bile talebi bir miktar artır (Niyet)
                    else:
                        piyasa.ticari_mallar[hammadde]["talep"] += ihtiyac // 2

    def uretim_yap(self):
        uretim_seviyesi = self.get_ortalama_seviye("Uretim")
        verimlilik_bonusu = 1 + (uretim_seviyesi / 100) + (self.ar_ge_seviyesi / 50)

        recete = self.urun_receteleri.get(self.urun_tipi)
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
            print(f"[{self.isim}] Üretim dep. {uretilecek_miktar} adet {self.urun_tipi} üretti.")

    def pazarlama_yap(self, piyasa):
        """Pazarlama departmanı, üretilen ürünleri satar ve piyasa arzını etkiler."""
        pazarlama_seviyesi = self.get_ortalama_seviye("Pazarlama")
        fiyat_artisi_orani = 1 + (pazarlama_seviyesi / 100)

        gelir = 0
        satilabilecek_miktar = int(self.urun_envanteri * (self.musteri_memnuniyeti / 100))

        if satilabilecek_miktar > 0:
            # PİYASA ETKİSİ: Satışa sunulan ürünler piyasadaki arzı artırır.
            piyasa.ticari_mallar[self.urun_tipi]["arz"] += satilabilecek_miktar

            urun_fiyati = piyasa.ticari_mallar[self.urun_tipi]["fiyat"] * fiyat_artisi_orani
            gelir = int(satilabilecek_miktar * urun_fiyati)
            self.urun_envanteri -= satilabilecek_miktar
            self.sermaye += gelir
            print(f"\n[{self.isim}] Pazarlama dep. {satilabilecek_miktar} adet ürün sattı (Gelir: {gelir} TL) ve piyasa arzını artırdı.")

        # Giderler (sabit ve maaşlar)
        toplam_maas = sum(c.maas for dep in self.departmanlar.values() for c in dep)
        gider = 50 + toplam_maas
        self.sermaye -= gider

        net_kar = gelir - gider
        return net_kar

class TrafikSistemi:
    def __init__(self):
        # Varsayımsal nüfus dağılımı ve yol kapasitesi
        self.nufus = {
            "Ev": 10000,
            "Şehir Merkezi": 500,
            "Sanayi Bölgesi": 5000 # Çalışan nüfus
        }
        self.yol_kapasitesi = 2500 # Aynı anda yolda olabilecek varsayımsal araç sayısı

    def get_yogunluk_katsayisi(self, saat):
        """Günün saatine göre trafik yoğunluk katsayısını (gecikme çarpanını) hesaplar."""
        hareket_halindeki_nufus = 0

        # Sabah işe gidiş (07:00 - 09:00)
        if 7 <= saat < 9:
            # Ev'deki nüfusun bir kısmı Sanayi Bölgesi'ne ve Şehir Merkezi'ne gidiyor
            hareket_halindeki_nufus = (self.nufus["Ev"] * 0.6)
        # Akşam işten dönüş (17:00 - 19:00)
        elif 17 <= saat < 19:
            # Sanayi Bölgesi ve Şehir Merkezi'ndeki nüfus Ev'e dönüyor
            hareket_halindeki_nufus = (self.nufus["Sanayi Bölgesi"] * 0.8) + (self.nufus["Şehir Merkezi"] * 0.5)
        # Öğle arası veya akşam dışarı çıkma (daha az yoğun)
        elif (12 <= saat < 14) or (20 <= saat < 22):
            hareket_halindeki_nufus = (self.nufus["Ev"] * 0.1) + (self.nufus["Şehir Merkezi"] * 0.3)
        else:
            # Normal saatlerdeki düşük yoğunluklu trafik
            hareket_halindeki_nufus = self.nufus["Ev"] * 0.05

        # Yoğunluk oranını hesapla (yoldaki araç sayısı / kapasite)
        yogunluk_orani = min(1.0, hareket_halindeki_nufus / self.yol_kapasitesi)

        # Katsayıyı 1 (gecikme yok) ile 3 (maksimum gecikme) arasında bir değere dönüştürelim.
        # Örneğin, kapasite %100 doluysa, süre 3 katına çıkar.
        katsayi = 1 + (yogunluk_orani * 2)
        return katsayi


class ZamanSistemi:
    def __init__(self):
        self.gun = 1
        self.saat = 8
        self.dakika = 0

    def __str__(self):
        return f"GÜN: {self.gun} | SAAT: {self.saat:02d}:{self.dakika:02d}"

    def zaman_ilerlet(self, gececek_dakika):
        """Zamanı belirtilen dakika kadar ilerletir ve gün/saat geçişlerini yönetir."""
        self.dakika += gececek_dakika

        saat_artisi, self.dakika = divmod(self.dakika, 60)
        self.saat += saat_artisi

        gun_artisi, self.saat = divmod(self.saat, 24)
        self.gun += gun_artisi

        return gun_artisi > 0, saat_artisi > 0 # Yeni gün veya yeni saat olup olmadığını döndürür

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
        for varlik, detaylar in self.yatirim_mallari.items():
            degisim_yuzdesi = detaylar["trend"] + (random.uniform(-detaylar.get("volatilite", 0.1), detaylar.get("volatilite", 0.1)))
            yeni_fiyat = detaylar["fiyat"] * (1 + degisim_yuzdesi)
            self.yatirim_mallari[varlik]["fiyat"] = max(1, int(yeni_fiyat))

        for mal, detaylar in self.ticari_mallar.items():
            self.fiyat_gecmisi[mal].append({"gun": gun, "fiyat": detaylar["fiyat"]})
            if len(self.fiyat_gecmisi[mal]) > 30:
                self.fiyat_gecmisi[mal].pop(0)

            detaylar["arz"] = max(10, detaylar["arz"] + random.randint(-10, 10))
            detaylar["talep"] = max(10, detaylar["talep"] + random.randint(-5, 5))

            fiyat_degisim_orani = (detaylar["talep"] - detaylar["arz"]) / 1000
            yeni_fiyat = detaylar["fiyat"] * (1 + fiyat_degisim_orani)
            self.ticari_mallar[mal]["fiyat"] = max(5, int(yeni_fiyat))

class Oyuncu:
    def __init__(self, isim, baslangic_konumu):
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
        self.portfoy = {}
        self.ticari_envanter = {}
        self.isletme = None
        self.metabolizma_hizi = 1.0
        self.metabolizma_etki_suresi = 0
        self.gazeteler = []
        self.otomasyon_modu = False
        self.universite_gun_sayaci = 0
        self.diploma = False
        self.sahip_olunan_evler = []
        self.iliskiler = []
        self.is_durumu = {"kariyer": None, "seviye": 0, "tecrube": 0}
        self.hastalik = None
        self.mevcut_konum = baslangic_konumu
        self.son_eylem_basarisiz = False

    def akilli_yemek_ye(self):
        """
        Karakterin akıllıca yemek yemesini sağlar.
        Önce envanteri kontrol eder, yiyecek yoksa markete gitmesi gerektiğini belirtir.
        Döneceği değer, hayat_simulasyonu.py'deki yönetici tarafından yorumlanacaktır.
        """
        yiyecekler = [esya for esya in self.envanter if "ev yemeği" in esya or "abur cubur" in esya]
        if yiyecekler:
            # Envanterde yiyecek var, ilk bulduğunu ye.
            # Dışarıdaki bir fonksiyonun `envanter_kullan` çağırması için yiyeceğin adını döndür.
            return yiyecekler[0]
        else:
            # Envanterde yiyecek yok, marketten alınması gerekiyor.
            # Dışarıdaki bir fonksiyonun `alisveris_yap` çağırması için `None` döndür.
            return None
