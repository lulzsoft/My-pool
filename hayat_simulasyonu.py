# -*- coding: utf-8 -*-

import random
import os
import time
import copy
import numpy as np

# Proje içi importlar
from varliklar import Oyuncu, Isletme, Calisan, NPC, Konum, Kariyer, Ev, ZamanSistemi, PiyasaSistemi, TrafikSistemi
import veri
from yapay_zeka import YapayZeka, durumu_al, odul_hesapla, EYLEMLER

# --- Sabitler ve Global Değişkenler ---
HIZLI_MOD = True # True ise, AI eğitimi için gecikmeleri ve çoğu çıktıyı atlar
KONUMLAR = {
    "Ev": Konum("Ev", ["Uyu", "Eğlen", "Kitap Oku", "Envanteri Kullan", "Spor Yap"]),
    "Şehir Merkezi": Konum("Şehir Merkezi", ["Alışveriş Yap", "İş Piyasası", "Emlakçıya Git", "Hastaneye Git", "Sosyal Etkileşime Gir"]),
    "Sanayi Bölgesi": Konum("Sanayi Bölgesi", ["İşe Git", "İş Kur / Yönet", "Ticaret Yap"])
}
emlak_ilanlari = []
dunya_sirketleri = []


def clear_screen():
    """Ekranı temizler."""
    if HIZLI_MOD: return
    os.system('cls' if os.name == 'nt' else 'clear')


def yapay_zeka_sirketlerini_olustur():
    """Oyun başlangıcında yapay zeka tarafından yönetilen rakip şirketleri oluşturur."""
    sirket_isimleri = ["TeknoDev", "ModaTrend", "MetalSan"]
    urun_tipleri = ["elektronik cihaz", "kıyafet", "elektronik cihaz"]

    for i in range(len(sirket_isimleri)):
        isim = sirket_isimleri[i]
        urun = urun_tipleri[i]
        sermaye = random.randint(15000, 30000)
        yeni_sirket = Isletme(isim, sermaye, urun, veri.DEPARTMANLAR, veri.URUN_RECETELERI)
        yeni_sirket.departmanlar["Uretim"].append(Calisan(f"{random.choice(veri.ISIM_LISTESI)}", "Uretim", seviye=3))
        yeni_sirket.departmanlar["Tedarik"].append(Calisan(f"{random.choice(veri.ISIM_LISTESI)}", "Tedarik", seviye=2))
        yeni_sirket.departmanlar["Pazarlama"].append(Calisan(f"{random.choice(veri.ISIM_LISTESI)}", "Pazarlama", seviye=4))
        dunya_sirketleri.append(yeni_sirket)
    if not HIZLI_MOD:
        print(f"\n--- Piyasa Rakipleri Oluşturuldu: {len(dunya_sirketleri)} şirket oyuna dahil oldu! ---")
        time.sleep(1)


def emlak_ilanlarini_guncelle():
    """Her 3 günde bir emlak ilanlarını rastgele evlerle yeniler."""
    global emlak_ilanlari
    emlak_ilanlari.clear()
    for _ in range(random.randint(3, 5)):
        tip_adi, tip_ozellikleri = random.choice(list(veri.EV_TİPLERİ.items()))
        metrekare = random.randint(tip_ozellikleri["min_m2"], tip_ozellikleri["max_m2"])
        olasi_eksiklikler = [k for k, v in veri.EV_EKSİKLİKLERİ.items() if v["kategori"] in tip_ozellikleri["kategoriler"]]
        eksiklik_sayisi = random.randint(0, min(5, len(olasi_eksiklikler)))
        secilen_eksiklikler = random.sample(olasi_eksiklikler, eksiklik_sayisi)
        yeni_ev = Ev(tip_adi, metrekare, secilen_eksiklikler, veri.EV_TİPLERİ, veri.EV_EKSİKLİKLERİ)
        emlak_ilanlari.append(yeni_ev)
    if not HIZLI_MOD:
        print("\n--- Emlak Piyasası Güncellendi! Yeni Evler Satışta! ---")
        time.sleep(0.5)


def zaman_etkilerini_isle(oyuncu, zaman, piyasa, gecen_dakika, gecen_gun_sayisi):
    """Geçen süre boyunca oyuncu ve dünya üzerindeki etkileri işler."""
    if gecen_dakika <= 0: return
    oyuncu.aclik = min(100, oyuncu.aclik + (gecen_dakika / 60.0) * (1 * oyuncu.metabolizma_hizi))
    oyuncu.hijyen = max(0, oyuncu.hijyen - (gecen_dakika / 60.0) * 0.5)
    if oyuncu.metabolizma_etki_suresi > 0:
        oyuncu.metabolizma_etki_suresi = max(0, oyuncu.metabolizma_etki_suresi - gecen_dakika)
        if oyuncu.metabolizma_etki_suresi == 0:
            oyuncu.metabolizma_hizi = 1.0
    if oyuncu.aclik >= 80:
        oyuncu.saglik -= (gecen_dakika / 60.0) * 0.5
        oyuncu.mutluluk -= (gecen_dakika / 60.0) * 0.5
    if oyuncu.hastalik:
        oyuncu.saglik = max(0, oyuncu.saglik - (gecen_dakika / 60.0) * 0.5)
        oyuncu.enerji = max(0, oyuncu.enerji - (gecen_dakika / 60.0) * 1)
    elif (oyuncu.saglik < 20 or oyuncu.hijyen < 10 or oyuncu.aclik > 90):
        if random.random() < (1 - (1 - (0.05 / 60))**gecen_dakika):
            oyuncu.hastalik = random.choice(["Grip", "Mide Rahatsızlığı", "Soğuk Algınlığı"])
            oyuncu.mutluluk -= 20
    if gecen_gun_sayisi > 0:
        for _ in range(int(gecen_gun_sayisi)):
            piyasa.gunluk_guncelle(zaman.gun)
            if oyuncu.isletme:
                oyuncu.isletme.tedarik_yap(piyasa)
                oyuncu.isletme.uretim_yap()
                oyuncu.isletme.pazarlama_yap(piyasa)
            for sirket in dunya_sirketleri:
                sirket.tedarik_yap(piyasa)
                sirket.uretim_yap()
                sirket.pazarlama_yap(piyasa)
            if zaman.gun % 365 == 0:
                oyuncu.yas += 1
            if oyuncu.universite_gun_sayaci > 0:
                oyuncu.universite_gun_sayaci = max(0, oyuncu.universite_gun_sayaci - 1)
                if oyuncu.universite_gun_sayaci == 0 and not oyuncu.diploma:
                    oyuncu.diploma = True
            if zaman.gun % 3 == 0:
                emlak_ilanlarini_guncelle()


def bar_gostergesi_olustur(label, deger):
    """Metin tabanlı bir ilerleme çubuğu oluşturur."""
    oran = deger / 100
    dolu = "█" * int(oran * 10)
    bos = "-" * (10 - len(dolu))
    return f"{label:<10}: [{dolu}{bos}] {int(deger)}%"


def durumu_goster(oyuncu, zaman, piyasa, adim=0, son_odul=0):
    """Oyuncunun anlık durumunu gösterir."""
    if HIZLI_MOD:
        print(f"\rAdım: {adim: <6} Gün: {zaman.gun: <4} Saat: {int(zaman.saat):02d} | Sağ: {oyuncu.saglik: <3.0f} Mut: {oyuncu.mutluluk: <3.0f} Ene: {oyuncu.enerji: <3.0f} Aç: {oyuncu.aclik: <3.0f} Para: {oyuncu.para: <6.0f} | Ödül: {son_odul: <6.2f}", end="")
        return
    clear_screen()
    print(f"--- {zaman} ---")
    print("--- GÜNCEL DURUM ---")
    print(bar_gostergesi_olustur("Sağlık", oyuncu.saglik))
    print(bar_gostergesi_olustur("Mutluluk", oyuncu.mutluluk))
    print(bar_gostergesi_olustur("Enerji", oyuncu.enerji))
    print(bar_gostergesi_olustur("Açlık", oyuncu.aclik))
    print(bar_gostergesi_olustur("Hijyen", oyuncu.hijyen))
    print("-" * 20)
    print(f"Para: {oyuncu.para} TL")
    # Diğer detaylar hızlı modda gösterilmez...


def eylemi_gerceklestir(oyuncu, eylem_adi, zaman, piyasa, trafik):
    """Yapay zeka tarafından seçilen bir eylemi gerçekleştirir."""
    # Bu fonksiyon, eski `eylem_sec` fonksiyonunun AI versiyonudur.
    # Kullanıcı girdisi yerine doğrudan `eylem_adi` alır.
    mumkun_eylemler_map = {
        "İşe Git": calis, "İş Piyasası": is_piyasasi, "Uyu": uyu,
        "Eğlen": eglen, "Eğitim Al (Okul/Üniversite)": okula_git,
        "Spor Yap": spor_yap, "Alışveriş Yap": alisveris_yap,
        "Kitap Oku": kitap_oku, "Envanteri Kullan": envanter_kullan,
        "Yatırım Yap": yatirim_yap,
        "İş Kur / Yönet": lambda o, z, p, t: is_kur(o) if o.isletme is None else isletmeyi_yonet(o, p),
        "Ticaret Yap": ticaret_yap, "Gazete Oku": gazete_oku,
        "Emlakçıya Git": emlakciya_git, "Sosyal Etkileşime Gir": sosyal_etkilesim,
        "Hastaneye Git": hastaneye_git, "Ulaşım": ulasim_yap
    }

    fonksiyon = mumkun_eylemler_map.get(eylem_adi)
    if fonksiyon:
        # AI kontrolü için tasarlanmış fonksiyonlara AI flag'i ekle
        if eylem_adi in ["İş Piyasası", "Hastaneye Git", "Alışveriş Yap", "Ulaşım"]:
             return fonksiyon(oyuncu, zaman=zaman, piyasa=piyasa, trafik=trafik, ai_kontrol=True)
        elif eylem_adi in ["Alışveriş Yap", "Ticaret Yap", "Yatırım Yap"]:
             return fonksiyon(oyuncu, zaman, piyasa)
        elif eylem_adi == "İş Kur / Yönet":
             return fonksiyon(oyuncu, zaman, piyasa, trafik)
        else:
             return fonksiyon(oyuncu, ai_kontrol=True) # Diğerlerine de ekle
    return 10 # Eğer eylem bulunamazsa veya geçersizse, 10 dakika harca


# --- Eylem Fonksiyonları (AI Kontrolü için güncellendi) ---
# Not: Birçok fonksiyonun `ai_kontrol` parametresi alması gerekecek.
# Bu, `input()` çağrılarını atlamak için kullanılır.

def is_piyasasi(oyuncu, **kwargs):
    # Basit AI mantığı: Eğer işi yoksa, her zaman ilk uygun işe başvurur.
    if not oyuncu.is_durumu["kariyer"]:
        uygun_isler = [k for ad, k in veri.KARİYERLER.items() if (k.diploma_gereksinimi and oyuncu.diploma) or not k.diploma_gereksinimi]
        if uygun_isler:
            secilen_kariyer = uygun_isler[0]
            if random.random() < 0.75:
                oyuncu.is_durumu = {"kariyer": secilen_kariyer, "seviye": 1, "tecrube": 0}
    return 120

def hastaneye_git(oyuncu, **kwargs):
    # Basit AI mantığı: Hastaysa ve parası varsa her zaman tedavi olur.
    if oyuncu.hastalik and oyuncu.para >= 200:
        oyuncu.para -= 200
        oyuncu.hastalik = None
        oyuncu.saglik = min(100, oyuncu.saglik + 20)
    return 180

def ulasim_yap(oyuncu, zaman, trafik, **kwargs):
    diger_konumlar = [k for k, v in KONUMLAR.items() if v.ad != oyuncu.mevcut_konum.ad]
    if not diger_konumlar: return 10
    hedef_konum_adi = random.choice(diger_konumlar) # AI rastgele bir yere gider
    # En ucuz ulaşımı seç (Otobüs)
    maliyet = 10
    sure = 45 * trafik.get_yogunluk_katsayisi(zaman.saat)
    if oyuncu.para >= maliyet:
        oyuncu.para -= maliyet
        oyuncu.mevcut_konum = KONUMLAR[hedef_konum_adi]
        return sure
    return 10

def calis(oyuncu, **kwargs):
    if not oyuncu.is_durumu["kariyer"] or oyuncu.hastalik or oyuncu.isletme: return 60
    if oyuncu.enerji >= 50:
        saat = 8
        kariyer = oyuncu.is_durumu["kariyer"]
        seviye_bilgisi = kariyer.get_seviye_bilgisi(oyuncu.is_durumu["seviye"])
        gunluk_kazanc = seviye_bilgisi["maas"] * saat
        oyuncu.para += gunluk_kazanc
        oyuncu.enerji -= 50
        oyuncu.mutluluk -= 15
        # Terfi mantığı basitlik için çıkarıldı
        return saat * 60
    return 60

def uyu(oyuncu, **kwargs):
    saat = 8 # AI her zaman 8 saat uyur
    oyuncu.enerji = min(100, oyuncu.enerji + saat * 8)
    return saat * 60

def envanter_kullan(oyuncu, **kwargs):
    yemekler = [esya for esya in oyuncu.envanter if "yemeği" in esya or "abur cubur" in esya]
    if yemekler:
        secilen_esya_adi = yemekler[0]
        esya_detay = veri.MAGAZA_ESYALARI[secilen_esya_adi]
        etki_alani = esya_detay.get('etki')
        deger = esya_detay['deger']
        mevcut_deger = getattr(oyuncu, etki_alani)
        setattr(oyuncu, etki_alani, min(100, max(0, mevcut_deger + deger)))
        oyuncu.envanter.remove(secilen_esya_adi)
    return 60

def alisveris_yap(oyuncu, zaman, piyasa, **kwargs):
    # AI'nin en temel ihtiyacı olan yemeği almasını sağla
    if oyuncu.para >= veri.MAGAZA_ESYALARI["ev yemeği"]["fiyat"]:
        oyuncu.para -= veri.MAGAZA_ESYALARI["ev yemeği"]["fiyat"]
        oyuncu.envanter.append("ev yemeği")
    return 60

# Henüz AI için tam olarak implemente edilmemiş diğer eylemler
def eglen(oyuncu, **kwargs): return 120
def okula_git(oyuncu, **kwargs): return 240
def spor_yap(oyuncu, **kwargs): return 60
def kitap_oku(oyuncu, **kwargs): return 60
def yatirim_yap(oyuncu, zaman, piyasa): return 120
def is_kur(oyuncu): return 180
def isletmeyi_yonet(oyuncu, piyasa): return 240
def ticaret_yap(oyuncu, zaman, piyasa): return 120
def gazete_oku(oyuncu, **kwargs): return 60
def emlakciya_git(oyuncu, **kwargs): return 120
def sosyal_etkilesim(oyuncu, **kwargs): return 60


def olum_gunlugu_yaz(oyuncu, zaman, neden, son_eylemler):
    """Karakter öldüğünde bir log dosyasına kayıt düşer."""
    with open("olum_gunlugu.log", "a", encoding="utf-8") as f:
        f.write("="*40 + "\n")
        f.write(f"ÖLÜM KAYDI\n")
        f.write(f"Tarih: {zaman}\n")
        f.write(f"Yaşanan Gün Sayısı: {zaman.gun}\n")
        f.write(f"Ölüm Nedeni: {neden}\n")
        f.write("\n--- SON DURUM ---\n")
        f.write(f"Sağlık: {oyuncu.saglik:.2f}\n")
        f.write(f"Enerji: {oyuncu.enerji:.2f}\n")
        f.write(f"Açlık: {oyuncu.aclik:.2f}\n")
        f.write(f"Mutluluk: {oyuncu.mutluluk:.2f}\n")
        f.write(f"Para: {oyuncu.para:.2f}\n")
        f.write("\n--- SON 5 EYLEM ---\n")
        for i, eylem in enumerate(son_eylemler, 1):
            f.write(f"{i}. {eylem}\n")
        f.write("="*40 + "\n\n")


# --- Ana Oyun Döngüsü ---

def main():
    """Ana AI eğitim döngüsü."""
    oyuncu = Oyuncu("AI Karakter", KONUMLAR["Ev"])
    zaman = ZamanSistemi()
    piyasa = PiyasaSistemi()
    trafik = TrafikSistemi()

    # AI kurulumu
    durum_boyutu = len(durumu_al(oyuncu, zaman, piyasa))
    eylem_boyutu = len(EYLEMLER)
    ai = YapayZeka(durum_boyutu, eylem_boyutu)
    ai.tecrubeyi_yukle()

    emlak_ilanlarini_guncelle()
    yapay_zeka_sirketlerini_olustur()

    oyun_bitti = False
    adim = 0
    son_odul = 0
    son_eylemler = []

    while not oyun_bitti:
        durumu_goster(oyuncu, zaman, piyasa, adim, son_odul)

        # 1. Mevcut durumu al
        mevcut_durum = durumu_al(oyuncu, zaman, piyasa)
        oyuncu_onceki = copy.deepcopy(oyuncu)

        # 2. Mümkün eylemleri belirle
        mumkun_eylemler = oyuncu.mevcut_konum.mumkun_eylemler + ["Ulaşım"]
        eylem_maskesi = np.array([eylem in mumkun_eylemler for eylem in EYLEMLER])

        # Ek kısıtlamalar (örn: işi yoksa işe gidemez)
        if not oyuncu.is_durumu["kariyer"]:
            eylem_maskesi[EYLEMLER.index("İşe Git")] = False
        if oyuncu.is_durumu["kariyer"]:
             eylem_maskesi[EYLEMLER.index("İş Piyasası")] = False

        # --- Cerrahi Müdahale: Hayatta Kalma İçgüdüsü Zorlaması (Tüm Senaryolar) ---
        if oyuncu.aclik > 75:
            envanterde_yemek_var = any("yemeği" in s or "abur cubur" in s for s in oyuncu.envanter)
            # Kritik açlıkta alakasız eylemler her zaman yasaktır.
            for eylem_adi in ["Uyu", "Eğlen", "Spor Yap", "Kitap Oku", "Yatırım Yap", "Ticaret Yap", "Emlakçıya Git"]:
                if eylem_adi in EYLEMLER:
                    eylem_maskesi[EYLEMLER.index(eylem_adi)] = False

            # Senaryo 1: Envanterde yemek var ve evde. Çözüm: YE.
            if envanterde_yemek_var and oyuncu.mevcut_konum.ad == "Ev":
                eylem_maskesi[:] = False
                eylem_maskesi[EYLEMLER.index("Envanteri Kullan")] = True
            # Senaryo 2: Yemek yok ama markete gidip alacak kadar para var (30 TL). Çözüm: Markete GİT ve AL.
            elif not envanterde_yemek_var and oyuncu.para >= 30:
                if oyuncu.mevcut_konum.ad != "Şehir Merkezi":
                    eylem_maskesi[:] = False
                    eylem_maskesi[EYLEMLER.index("Ulaşım")] = True
                else: # Şehir Merkezi'nde
                    eylem_maskesi[:] = False
                    eylem_maskesi[EYLEMLER.index("Alışveriş Yap")] = True
            # Senaryo 3: Yeterli para yok. Çözüm: PARA KAZAN.
            else:
                # İşin varsa, Sanayi Bölgesi'ne git ve çalış.
                if oyuncu.is_durumu["kariyer"]:
                    if oyuncu.mevcut_konum.ad != "Sanayi Bölgesi":
                        eylem_maskesi[:] = False
                        eylem_maskesi[EYLEMLER.index("Ulaşım")] = True
                    else: # Sanayi Bölgesi'nde
                        eylem_maskesi[:] = False
                        eylem_maskesi[EYLEMLER.index("İşe Git")] = True
                # İşin yoksa, Şehir Merkezi'ne git ve iş ara.
                else:
                    if oyuncu.mevcut_konum.ad != "Şehir Merkezi":
                        eylem_maskesi[:] = False
                        eylem_maskesi[EYLEMLER.index("Ulaşım")] = True
                    else: # Şehir Merkezi'nde
                        eylem_maskesi[:] = False
                        eylem_maskesi[EYLEMLER.index("İş Piyasası")] = True


        # 3. AI eylem seçsin
        eylem_index = ai.eylem_sec(mevcut_durum, eylem_maskesi)
        secilen_eylem_adi = EYLEMLER[eylem_index]
        son_eylemler.append(secilen_eylem_adi)
        if len(son_eylemler) > 5:
            son_eylemler.pop(0)

        # 4. Eylemi gerçekleştir
        harcanacak_dakika = eylemi_gerceklestir(oyuncu, secilen_eylem_adi, zaman, piyasa, trafik)

        # 5. Zamanı ilerlet ve etkileri işle
        onceki_gun = zaman.gun
        if harcanacak_dakika > 0:
            zaman.zaman_ilerlet(harcanacak_dakika)
        gecen_gun_sayisi = zaman.gun - onceki_gun
        zaman_etkilerini_isle(oyuncu, zaman, piyasa, harcanacak_dakika, gecen_gun_sayisi)

        # 6. Yeni durumu ve ödülü al
        oyun_bitti = oyuncu.saglik <= 0
        yeni_durum = durumu_al(oyuncu, zaman, piyasa)
        odul = odul_hesapla(oyuncu_onceki, oyuncu, secilen_eylem_adi, harcanacak_dakika)
        son_odul = odul

        # 7. Tecrübeyi hafızaya kaydet
        ai.tecrubeyi_hatirla(mevcut_durum, eylem_index, odul, yeni_durum, oyun_bitti)

        # 8. Ağı eğit
        ai.ogren()

        # 9. Günü bitir ve tecrübeyi kaydet
        if gecen_gun_sayisi > 0:
            print(f"\n--- Gün {onceki_gun} Bitti. Toplam Adım: {adim}, Epsilon: {ai.epsilon:.4f} ---")
            ai.tecrubeyi_kaydet()
            if not HIZLI_MOD: time.sleep(2)

        adim += 1

        if oyun_bitti:
            print(f"\nOYUN BITTI! Karakter {zaman.gun} gün yaşadı.")
            olum_gunlugu_yaz(oyuncu, zaman, "Açlık/Sağlık", son_eylemler)
            # Reenkarnasyon: Oyunu sıfırla ama AI öğrenmeye devam etsin
            oyuncu = Oyuncu("AI Karakter", KONUMLAR["Ev"])
            zaman = ZamanSistemi()
            oyun_bitti = False
            son_eylemler.clear() # Listeyi temizle


if __name__ == "__main__":
    main()
