# -*- coding: utf-8 -*-

import random
import os
import time
import copy

# Hızlı mod anahtarı. True ise, time.sleep() çağrıları atlanır.
HIZLI_MOD = False

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

from varliklar import Oyuncu, Isletme, Calisan, NPC, Konum, Kariyer, Ev, ZamanSistemi, PiyasaSistemi, TrafikSistemi
from yapay_zeka import YapayZeka
import veri

# Ulaşım ve Konum Sistemi
KONUMLAR = {
    "Ev": Konum("Ev", ["Uyu", "Eğlen", "Kitap Oku", "Envanteri Kullan", "Spor Yap"]),
    "Şehir Merkezi": Konum("Şehir Merkezi", ["Alışveriş Yap", "İş Piyasası", "Emlakçıya Git", "Hastaneye Git", "Sosyal Etkileşime Gir"]),
    "Sanayi Bölgesi": Konum("Sanayi Bölgesi", ["İşe Git", "İş Kur / Yönet", "Ticaret Yap"])
}

# Global Emlak İlanları
emlak_ilanlari = []
# Global AI Şirketleri
dunya_sirketleri = []


def yapay_zeka_sirketlerini_olustur():
    """Oyun başlangıcında yapay zeka tarafından yönetilen rakip şirketleri oluşturur."""
    global dunya_sirketleri
    dunya_sirketleri.clear()
    sirket_isimleri = ["TeknoDev", "ModaTrend", "MetalSan"]
    urun_tipleri = ["elektronik cihaz", "kıyafet", "elektronik cihaz"]

    for i in range(len(sirket_isimleri)):
        isim = sirket_isimleri[i]
        urun = urun_tipleri[i]
        sermaye = random.randint(15000, 30000)
        yeni_sirket = Isletme(isim, sermaye, urun, veri.DEPARTMANLAR, veri.URUN_RECETELERI)
        # AI şirketlerine başlangıçta daha fazla çalışan verelim ki aktif olsunlar
        yeni_sirket.departmanlar["Uretim"].append(Calisan(f"{random.choice(veri.ISIM_LISTESI)}", "Uretim", seviye=3))
        yeni_sirket.departmanlar["Tedarik"].append(Calisan(f"{random.choice(veri.ISIM_LISTESI)}", "Tedarik", seviye=2))
        yeni_sirket.departmanlar["Pazarlama"].append(Calisan(f"{random.choice(veri.ISIM_LISTESI)}", "Pazarlama", seviye=4))
        dunya_sirketleri.append(yeni_sirket)
    if not HIZLI_MOD:
        print(f"\n--- Piyasa Rakipleri Oluşturuldu: {len(dunya_sirketleri)} şirket oyuna dahil oldu! ---")
        time.sleep(2)


def emlak_ilanlarini_guncelle():
    """Her 3 günde bir emlak ilanlarını rastgele evlerle yeniler."""
    global emlak_ilanlari
    emlak_ilanlari.clear()

    for _ in range(random.randint(3, 5)): # 3 ila 5 arası yeni ilan
        tip_adi, tip_ozellikleri = random.choice(list(veri.EV_TİPLERİ.items()))
        metrekare = random.randint(tip_ozellikleri["min_m2"], tip_ozellikleri["max_m2"])

        olasi_eksiklikler = [k for k, v in veri.EV_EKSİKLİKLERİ.items() if v["kategori"] in tip_ozellikleri["kategoriler"]]
        eksiklik_sayisi = random.randint(0, min(5, len(olasi_eksiklikler)))
        secilen_eksiklikler = random.sample(olasi_eksiklikler, eksiklik_sayisi)

        yeni_ev = Ev(tip_adi, metrekare, secilen_eksiklikler, veri.EV_TİPLERİ, veri.EV_EKSİKLİKLERİ)
        emlak_ilanlari.append(yeni_ev)
    if not HIZLI_MOD:
        print("\n--- Emlak Piyasası Güncellendi! Yeni Evler Satışta! ---")
        time.sleep(1)


def zaman_etkilerini_isle(oyuncu, zaman, piyasa, gecen_dakika, gecen_gun_sayisi):
    """Geçen süre boyunca oyuncu ve dünya üzerindeki etkileri işler."""
    if gecen_dakika <= 0:
        return

    # Dakika bazlı stat güncellemeleri
    oyuncu.aclik = min(100, oyuncu.aclik + (gecen_dakika / 60.0) * (1 * oyuncu.metabolizma_hizi))
    oyuncu.hijyen = max(0, oyuncu.hijyen - (gecen_dakika / 60.0) * 0.5)

    # Metabolizma etkisini yönet (süre dakika bazlı)
    if oyuncu.metabolizma_etki_suresi > 0:
        oyuncu.metabolizma_etki_suresi = max(0, oyuncu.metabolizma_etki_suresi - gecen_dakika)
        if oyuncu.metabolizma_etki_suresi == 0:
            oyuncu.metabolizma_hizi = 1.0
            if not HIZLI_MOD:
                print("\nMetabolizman normale döndü.")

    # Kriz durumları
    if oyuncu.aclik >= 80:
        oyuncu.saglik -= (gecen_dakika / 60.0) * 0.5
        oyuncu.mutluluk -= (gecen_dakika / 60.0) * 0.5

    # Hastalık mekaniği
    if oyuncu.hastalik:
        oyuncu.saglik = max(0, oyuncu.saglik - (gecen_dakika / 60.0) * 0.5)
        oyuncu.enerji = max(0, oyuncu.enerji - (gecen_dakika / 60.0) * 1)
    elif (oyuncu.saglik < 20 or oyuncu.hijyen < 10 or oyuncu.aclik > 90):
        saatlik_sans = 0.05
        dakikalik_sans = saatlik_sans / 60
        toplam_sans = 1 - (1 - dakikalik_sans)**gecen_dakika
        if random.random() < toplam_sans:
            oyuncu.hastalik = random.choice(["Grip", "Mide Rahatsızlığı", "Soğuk Algınlığı"])
            if not HIZLI_MOD:
                print(f"\nKÖTÜ HABER! Kendine iyi bakmadığın için '{oyuncu.hastalik}' oldun.")
            oyuncu.mutluluk -= 20

    # Günlük güncellemeler
    if gecen_gun_sayisi > 0:
        if not HIZLI_MOD:
            print(f"\n--- {gecen_gun_sayisi} Gün Geçti ---")
        for _ in range(gecen_gun_sayisi):
            piyasa.gunluk_guncelle(zaman.gun)

            # Oyuncunun şirketini işle
            if oyuncu.isletme:
                oyuncu.isletme.tedarik_yap(piyasa)
                oyuncu.isletme.uretim_yap()
                net_kar = oyuncu.isletme.pazarlama_yap(piyasa)

            # AI şirketlerini işle
            for sirket in dunya_sirketleri:
                sirket.tedarik_yap(piyasa)
                sirket.uretim_yap()
                sirket.pazarlama_yap(piyasa)

            if zaman.gun % 365 == 0:
                oyuncu.yas += 1
                if not HIZLI_MOD:
                    print(f"\nDoğum günün kutlu olsun! Artık {oyuncu.yas} yaşındasın.")

            if oyuncu.universite_gun_sayaci > 0:
                oyuncu.universite_gun_sayaci = max(0, oyuncu.universite_gun_sayaci - 1)
                if oyuncu.universite_gun_sayaci == 0 and not oyuncu.diploma:
                    oyuncu.diploma = True
                    if not HIZLI_MOD:
                        print("\nTEBRİKLER! Üniversiteyi bitirdin ve diplomanı aldın!")

            if zaman.gun % 3 == 0:
                emlak_ilanlarini_guncelle()

def yapay_zeka_eylem_yonetici(oyuncu, zaman, piyasa, trafik, karar):
    """
    Yapay zekanın verdiği kararı yorumlar, gerekli koşulları kontrol eder
    (örn: konum değiştirme) ve ilgili eylemi tetikler.
    """
    if not HIZLI_MOD:
        print(f"\n>>> AI Kararı: {karar}")
        time.sleep(1)

    # Eylem ve gerektirdiği konum eşleşmesi
    eylem_konum_map = {
        'Çalış': "Sanayi Bölgesi",
        'Yemek Ye': "Şehir Merkezi", # Markete gitmek için
        'Temizlen': "Ev",
        'Eğitim Al': "Şehir Merkezi",
        'Uyu': "Ev",
        'Kitap Oku': "Ev",
        'İş Kur/Yönet': "Sanayi Bölgesi",
    }

    # Eylem ve fonksiyon eşleşmesi
    eylem_fonksiyon_map = {
        'Çalış': calis,
        'Yemek Ye': lambda o,z,p,t: alisveris_yap(o, z, p, otomasyon_hedef="ev yemeği"),
        'Temizlen': lambda o,z,p,t: envanter_kullan(o, override_secim="sabun"),
        'Eğitim Al': okula_git,
        'Uyu': uyu,
        'Kitap Oku': kitap_oku,
        'İş Kur/Yönet': lambda o, z, p, t: is_kur(o, ai_kontrol=True) if o.isletme is None else isletmeyi_yonet(o, p, ai_kontrol=True),
    }

    hedef_konum = eylem_konum_map.get(karar)

    # 1. Adım: Konum kontrolü ve gerekirse ulaşım
    if hedef_konum and oyuncu.mevcut_konum.ad != hedef_konum:
        if not HIZLI_MOD:
            print(f"'{karar}' eylemi için '{hedef_konum}' konumuna gidiliyor...")
            time.sleep(1)
        # Hedef konumu bul ve oraya git
        diger_konumlar = [k for k, v in KONUMLAR.items() if v.ad != oyuncu.mevcut_konum.ad]
        if hedef_konum in diger_konumlar:
            return ulasim_yap(oyuncu, zaman, trafik, hedef_konum_adi=hedef_konum)
        else:
            if not HIZLI_MOD:
                print("Hata: Hedef konum bulunamadı.")
            return 10 # Hata durumunda zamanı biraz ilerlet

    # 2. Adım: Eylemi gerçekleştir
    if karar in eylem_fonksiyon_map:
        fonksiyon = eylem_fonksiyon_map[karar]
        # Bazi fonksiyonlarin argumanlari farkli, bu yuzden lambda ile sarmaladik
        return fonksiyon(oyuncu, zaman, piyasa, trafik)
    else:
        if not HIZLI_MOD:
            print(f"Bilinmeyen AI kararı: {karar}")
        return 10


def gunluk_loglari_yaz(gun, loglar):
    """Günlük aktiviteleri bir log dosyasına yazar."""
    with open("gunluk_aktivite.log", "a", encoding="utf-8") as f:
        f.write(f"--- GÜN {gun} AKTİVİTELERİ ---\n")
        for log in loglar:
            f.write(log + "\n")
        f.write("\n")

def main():
    """Ana oyun fonksiyonu. Reenkarnasyon döngüsü içerir."""
    hayat_sayaci = 0
    yapay_zeka = YapayZeka()
    yapay_zeka.yukle() # Kayıtlı tecrübeyi yükle

    while True:
        hayat_sayaci += 1
        clear_screen()
        if not HIZLI_MOD:
            print(f"--- HAYAT #{hayat_sayaci} BAŞLIYOR ---")
            time.sleep(2)

        isim = f"Yapay Zeka #{hayat_sayaci}"
        oyuncu = Oyuncu(isim, KONUMLAR["Ev"])

        aile_isim = f"{random.choice(veri.ISIM_LISTESI)} {random.choice(veri.SOYISIM_LISTESI)}"
        arkadas_isim = f"{random.choice(veri.ISIM_LISTESI)} {random.choice(veri.SOYISIM_LISTESI)}"
        oyuncu.iliskiler.append(NPC(aile_isim, "Aile"))
        oyuncu.iliskiler.append(NPC(arkadas_isim, "Arkadaş"))

        emlak_ilanlarini_guncelle()
        yapay_zeka_sirketlerini_olustur()

        zaman = ZamanSistemi()
        piyasa = PiyasaSistemi()
        trafik = TrafikSistemi()

        gunluk_loglar = []
        oyun_bitti = False
        while not oyun_bitti:
            durumu_goster(oyuncu, zaman, piyasa)

            mevcut_durum_kopya = copy.deepcopy(oyuncu)
            mevcut_zaman_kopya = copy.deepcopy(zaman)
            durum_dict = {'oyuncu': mevcut_durum_kopya, 'zaman': mevcut_zaman_kopya}

            eylem_index, ai_karari = yapay_zeka.karar_ver(mevcut_durum_kopya, mevcut_zaman_kopya)

            onceki_gun = zaman.gun
            harcanacak_dakika = yapay_zeka_eylem_yonetici(oyuncu, zaman, piyasa, trafik, ai_karari)

            if harcanacak_dakika > 0:
                zaman.zaman_ilerlet(harcanacak_dakika)
                gecen_gun_sayisi = zaman.gun - onceki_gun
                zaman_etkilerini_isle(oyuncu, zaman, piyasa, harcanacak_dakika, gecen_gun_sayisi)
            else:
                zaman.zaman_ilerlet(10)

            sonraki_durum_dict = {'oyuncu': oyuncu, 'zaman': zaman}
            odul = odul_hesapla(mevcut_durum_kopya, oyuncu, ai_karari)

            log_mesaji = (f"[{zaman}] Eylem: {ai_karari}, Süre: {harcanacak_dakika}dk, Ödül: {odul:.2f}, "
                          f"Sağlık: {oyuncu.saglik:.1f}, Para: {oyuncu.para}, Epsilon: {yapay_zeka.epsilon:.3f}")
            gunluk_loglar.append(log_mesaji)
            if not HIZLI_MOD:
                print(f"--- Eylem Sonucu: Ödül = {odul}, Epsilon = {yapay_zeka.epsilon:.2f} ---")

            if onceki_gun != zaman.gun:
                gunluk_loglari_yaz(onceki_gun, gunluk_loglar)
                gunluk_loglar = []
                yapay_zeka.kaydet() # Her gün sonunda tecrübeyi kaydet

            yapay_zeka.ogren(durum_dict, eylem_index, odul, sonraki_durum_dict)

            if oyuncu.saglik <= 0:
                oyun_bitti = True
                yapay_zeka.kaydet() # Ölmeden hemen önce son bir kez kaydet
                if not HIZLI_MOD:
                    print(f"\n--- HAYAT #{hayat_sayaci} SONA ERDİ (Yaş: {oyuncu.yas}, Gün: {zaman.gun}) ---")
                gunluk_loglari_yaz(zaman.gun, gunluk_loglar) # Son günün loglarını yaz
                gunluk_loglar = []
                if not HIZLI_MOD:
                    time.sleep(3)

            if not HIZLI_MOD:
                time.sleep(1)


def odul_hesapla(onceki_durum, mevcut_durum, yapilan_eylem):
    """
    İki durum arasındaki farka ve yapılan eyleme göre bir ödül/ceza puanı hesaplar.
    """
    odul = 0

    # Para değişiklikleri
    para_farki = mevcut_durum.para - onceki_durum.para
    if para_farki > 0:
        odul += 1

    # Stat değişiklikleri
    if mevcut_durum.saglik > onceki_durum.saglik or mevcut_durum.mutluluk > onceki_durum.mutluluk:
        odul += 2

    # Cezalar
    if mevcut_durum.aclik > 70:
        odul -= 5
    if mevcut_durum.saglik < 40 or mevcut_durum.mutluluk < 40 or mevcut_durum.enerji < 40:
        odul -= 5
    if mevcut_durum.saglik <= 0:
        odul -= 100

    # Eyleme özel ödüller
    if yapilan_eylem in ['Eğitim Al', 'Kitap Oku', 'Sosyal Etkileşime Gir']:
        odul += 5

    # Yatırım eylemi için daha akıllı ödül/ceza
    if yapilan_eylem == 'Yatırım Yap':
        if para_farki > 0: # Yatırımdan kar ettiyse
            odul += 10
        elif onceki_durum.para < 500: # Az parayla yatırım yapmaya çalışırsa
            odul -= 10
        else: # Nötr veya zararla sonuçlanırsa
            odul -= 2

    if yapilan_eylem == 'Hastaneye Git' and onceki_durum.hastalik is not None and mevcut_durum.hastalik is None:
        odul += 20

    return odul


def bar_gostergesi_olustur(label, deger, max_deger=100, uzunluk=10):
    """Metin tabanlı bir ilerleme çubuğu oluşturur."""
    oran = deger / max_deger
    dolu_uzunluk = int(oran * uzunluk)
    bos_uzunluk = uzunluk - dolu_uzunluk
    bar = "█" * dolu_uzunluk + "-" * bos_uzunluk
    return f"{label:<10}: [{bar}] {int(deger)}%"

def durumu_goster(oyuncu, zaman, piyasa):
    """Oyuncunun anlık durumunu gösterir. Hızlı mod için farklı bir arayüz kullanır."""
    if HIZLI_MOD:
        # Hızlı mod için tek satırlık, anlık güncellenen arayüz
        hayat_bilgisi = f"Hayat: {oyuncu.isim.split('#')[-1].strip()}"
        zaman_bilgisi = f"Gün: {zaman.gun} Saat: {zaman.saat:02d}:00"
        para_bilgisi = f"Para: {oyuncu.para} TL"

        saglik_bar = bar_gostergesi_olustur("Sğl", oyuncu.saglik, uzunluk=5)
        mutluluk_bar = bar_gostergesi_olustur("Mtl", oyuncu.mutluluk, uzunluk=5)
        enerji_bar = bar_gostergesi_olustur("Enr", oyuncu.enerji, uzunluk=5)
        aclik_bar = bar_gostergesi_olustur("Açlk", oyuncu.aclik, uzunluk=5)

        # \r (carriage return) imleci satır başına alır, böylece bir sonraki print üzerine yazar.
        # end='' ile de print'in otomatik yeni satıra geçmesi engellenir.
        print(f"\r{hayat_bilgisi} | {zaman_bilgisi} | {para_bilgisi} | {saglik_bar} | {mutluluk_bar} | {enerji_bar} | {aclik_bar}", end='')
    else:
        # Normal (yavaş) mod için detaylı arayüz
        clear_screen()
        print(f"--- {zaman} ---")
        print("--- GÜNCEL DURUM ---")
        print(f"İsim: {oyuncu.isim}  |  Yaş: {oyuncu.yas}  |  Diploma: {'Var' if oyuncu.diploma else 'Yok'}")
        print(f"Konum: {oyuncu.mevcut_konum.ad}  |  Sağlık Durumu: {oyuncu.hastalik if oyuncu.hastalik else 'Sağlıklı'}")
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

        if oyuncu.iliskiler:
            print("-" * 20)
            print("Sosyal Çevren:")
            for npc in oyuncu.iliskiler:
                print(f" - {npc}")

        print("--------------------")

def is_piyasasi(oyuncu):
    """İş piyasası menüsünü yönetir, iş bulma ve işten ayrılma işlemleri."""
    if not HIZLI_MOD:
        print("\n--- İŞ PİYASASI ---")

    if oyuncu.is_durumu["kariyer"]:
        kariyer = oyuncu.is_durumu["kariyer"]
        seviye_bilgisi = kariyer.get_seviye_bilgisi(oyuncu.is_durumu["seviye"])
        if not HIZLI_MOD:
            print(f"Mevcut İşin: {seviye_bilgisi['unvan']} ({kariyer.ad})")
            print("1: İşten Ayrıl")
        secim = input("Seçimin: ")
        if secim == '1':
            if not HIZLI_MOD:
                print(f"'{kariyer.ad}' kariyerinden ayrıldın.")
            oyuncu.is_durumu = {"kariyer": None, "seviye": 0, "tecrube": 0}
        if not HIZLI_MOD:
            time.sleep(2)
        return 60

    else:
        if not HIZLI_MOD:
            print("Mevcut İş İlanları:")
        uygun_isler = []
        for ad, kariyer in veri.KARİYERLER.items():
            if (kariyer.diploma_gereksinimi and oyuncu.diploma) or not kariyer.diploma_gereksinimi:
                uygun_isler.append(kariyer)

        if not uygun_isler:
            if not HIZLI_MOD:
                print("Sana uygun hiç iş ilanı yok.")
        else:
            for i, kariyer in enumerate(uygun_isler):
                baslangic_maasi = kariyer.get_seviye_bilgisi(1)["maas"] * 8
                if not HIZLI_MOD:
                    print(f"{i+1}: {kariyer.ad} (Başlangıç Günlük Maaş: {baslangic_maasi} TL)")

            try:
                secim_is = int(input(f"Başvurmak istediğin işin numarasını gir (1-{len(uygun_isler)}): "))
                if 0 < secim_is <= len(uygun_isler):
                    secilen_kariyer = uygun_isler[secim_is - 1]
                    # Mülakat simülasyonu (basit rastgele şans)
                    if random.random() < 0.75: # %75 işe alınma şansı
                        if not HIZLI_MOD:
                            print(f"Tebrikler! '{secilen_kariyer.ad}' olarak işe alındın.")
                        oyuncu.is_durumu["kariyer"] = secilen_kariyer
                        oyuncu.is_durumu["seviye"] = 1
                        oyuncu.is_durumu["tecrube"] = 0
                    else:
                        if not HIZLI_MOD:
                            print("Mülakat başarısız oldu, işe alınmadın.")
                        oyuncu.mutluluk -= 10
                else:
                    if not HIZLI_MOD:
                        print("Geçersiz seçim.")
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")

        if not HIZLI_MOD:
            time.sleep(3)
        return 120


def hastaneye_git(oyuncu):
    """Hastaneye giderek hastalıkları tedavi etme eylemi."""
    if not HIZLI_MOD:
        print("\n--- HASTANE ---")
    if not oyuncu.hastalik:
        if not HIZLI_MOD:
            print("Herhangi bir hastalığın yok.")
            time.sleep(2)
        return 60

    tedavi_ucreti = 200
    if not HIZLI_MOD:
        print(f"'{oyuncu.hastalik}' için tedavi ücreti: {tedavi_ucreti} TL.")
    if oyuncu.para >= tedavi_ucreti:
        onay = input("Tedavi olmak istiyor musun? (e/h): ").lower()
        if onay == 'e':
            oyuncu.para -= tedavi_ucreti
            oyuncu.hastalik = None
            oyuncu.saglik = min(100, oyuncu.saglik + 20) # Tedavi sonrası sağlık bonusu
            if not HIZLI_MOD:
                print("Tedavi başarılı oldu! Artık sağlıklısın.")
    else:
        if not HIZLI_MOD:
            print("Tedavi için yeterli paran yok.")

    if not HIZLI_MOD:
        time.sleep(2)
    return 180


def sosyal_etkilesim(oyuncu):
    """NPC'lerle sosyal etkileşim menüsünü yönetir."""
    if not HIZLI_MOD:
        print("\n--- SOSYAL ETKİLEŞİM ---")
    if not oyuncu.iliskiler:
        if not HIZLI_MOD:
            print("Etkileşime girecek kimsen yok.")
            time.sleep(2)
        return 60

    for i, npc in enumerate(oyuncu.iliskiler):
        if not HIZLI_MOD:
            print(f"{i+1}: {npc.isim} ({npc.iliski_turu})")

    try:
        secim_npc = int(input(f"Kiminle etkileşime girmek istersin? (1-{len(oyuncu.iliskiler)}): "))
        if 0 < secim_npc <= len(oyuncu.iliskiler):
            secilen_npc = oyuncu.iliskiler[secim_npc - 1]
            if not HIZLI_MOD:
                print(f"\n{secilen_npc.isim} ile ne yapmak istersin?")
                print("1: Sohbet Et (İlişki +2, Mutluluk +5)")
                print("2: Hediye Al (50 TL) (İlişki +10)")
                print("3: Birlikte Vakit Geçir (3 Saat, 100 TL) (İlişki +15, Mutluluk +20)")

            secim_eylem = input("Seçimin: ")
            if secim_eylem == '1':
                secilen_npc.iliski_seviyesi = min(100, secilen_npc.iliski_seviyesi + 2)
                oyuncu.mutluluk = min(100, oyuncu.mutluluk + 5)
                if not HIZLI_MOD:
                    print(f"{secilen_npc.isim} ile sohbet ettin.")
                return 60
            elif secim_eylem == '2' and oyuncu.para >= 50:
                oyuncu.para -= 50
                secilen_npc.iliski_seviyesi = min(100, secilen_npc.iliski_seviyesi + 10)
                if not HIZLI_MOD:
                    print(f"{secilen_npc.isim}'a hediye aldın.")
                return 60
            elif secim_eylem == '3' and oyuncu.para >= 100:
                oyuncu.para -= 100
                secilen_npc.iliski_seviyesi = min(100, secilen_npc.iliski_seviyesi + 15)
                oyuncu.mutluluk = min(100, oyuncu.mutluluk + 20)
                if not HIZLI_MOD:
                    print(f"{secilen_npc.isim} ile 3 saat vakit geçirdin.")
                return 180
            else:
                if not HIZLI_MOD:
                    print("Geçersiz eylem veya yetersiz para.")
                return 60
    except (ValueError, IndexError):
        if not HIZLI_MOD:
            print("Geçersiz seçim.")

    if not HIZLI_MOD:
        time.sleep(2)
    return 60


def emlakciya_git(oyuncu):
    """Emlakçıya giderek ev alım satım ve yönetim işlemlerini yapar."""
    if not HIZLI_MOD:
        print("\n--- EMLAKÇI ---")
        print("1: Satılık İlanları Görüntüle")
        print("2: Sahip Olduğun Evleri Yönet")
        print("3: Ev Sat")

    secim = input("Ne yapmak istersin? (1-3), çıkmak için 0): ")

    if secim == '1':
        if not emlak_ilanlari:
            if not HIZLI_MOD:
                print("Şu anda hiç satılık ev ilanı yok.")
        else:
            if not HIZLI_MOD:
                print("\n--- SATILIK EV İLANLARI ---")
            for i, ev in enumerate(emlak_ilanlari):
                if not HIZLI_MOD:
                    print(f"{i+1}: {ev.tip} ({ev.metrekare} m²) - Fiyat: {ev.alis_fiyati} TL")

            try:
                secim_ev = int(input(f"Satın almak istediğin evin numarasını gir (1-{len(emlak_ilanlari)}), çıkmak için 0): "))
                if secim_ev > 0:
                    secilen_ev = emlak_ilanlari[secim_ev - 1]
                    if oyuncu.para >= secilen_ev.alis_fiyati:
                        oyuncu.para -= secilen_ev.alis_fiyati
                        oyuncu.sahip_olunan_evler.append(secilen_ev)
                        emlak_ilanlari.pop(secim_ev - 1)
                        if not HIZLI_MOD:
                            print(f"Tebrikler! {secilen_ev.tip} satın aldın.")
                    else:
                        if not HIZLI_MOD:
                            print("Bu evi almak için yeterli paran yok.")
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")

    elif secim == '2':
        if not oyuncu.sahip_olunan_evler:
            if not HIZLI_MOD:
                print("Yönetilecek hiç evin yok.")
        else:
            if not HIZLI_MOD:
                print("\n--- EVLERİNİ YÖNET ---")
            for i, ev in enumerate(oyuncu.sahip_olunan_evler):
                if not HIZLI_MOD:
                    print(f"{i+1}: {ev}")

            try:
                secim_yonet = int(input(f"Yönetmek istediğin evin numarasını gir (1-{len(oyuncu.sahip_olunan_evler)}): "))
                if secim_yonet > 0:
                    secilen_ev = oyuncu.sahip_olunan_evler[secim_yonet - 1]
                    if not HIZLI_MOD:
                        print(f"\n--- {secilen_ev.tip} Yönetimi ---")
                        print("Eksiklikler:")
                    tamir_edilecekler = []
                    for eksik, durum in secilen_ev.eksiklikler.items():
                        durum_str = "Tamir Edilmiş" if durum else "Tamir Bekliyor"
                        maliyet = veri.EV_EKSİKLİKLERİ[eksik]["maliyet"]
                        if not HIZLI_MOD:
                            print(f" - {eksik}: {durum_str} (Maliyet: {maliyet} TL)")
                        if not durum:
                            tamir_edilecekler.append(eksik)

                    if not tamir_edilecekler:
                        if not HIZLI_MOD:
                            print("Bu evde tamir edilecek bir şey yok.")
                    else:
                        onay = input("Bu evdeki tüm eksiklikleri tamir ettirmek istiyor musun? (e/h): ").lower()
                        if onay == 'e':
                            toplam_maliyet = sum(veri.EV_EKSİKLİKLERİ[e]["maliyet"] for e in tamir_edilecekler)
                            if not HIZLI_MOD:
                                print(f"Toplam tamir maliyeti: {toplam_maliyet} TL.")
                            if oyuncu.para >= toplam_maliyet:
                                oyuncu.para -= toplam_maliyet
                                for eksik in tamir_edilecekler:
                                    secilen_ev.eksiklikler[eksik] = True
                                if not HIZLI_MOD:
                                    print("Usta çağrıldı ve tüm eksiklikler giderildi!")
                            else:
                                if not HIZLI_MOD:
                                    print("Tamir için yeterli paran yok.")
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")

    elif secim == '3':
        if not oyuncu.sahip_olunan_evler:
            if not HIZLI_MOD:
                print("Satacak hiç evin yok.")
        else:
            if not HIZLI_MOD:
                print("\n--- EV SAT ---")
            for i, ev in enumerate(oyuncu.sahip_olunan_evler):
                if not HIZLI_MOD:
                    print(f"{i+1}: {ev} - Potansiyel Satış Fiyatı: {ev.satis_fiyati} TL")

            try:
                secim_sat = int(input(f"Satmak istediğin evin numarasını gir (1-{len(oyuncu.sahip_olunan_evler)}): "))
                if secim_sat > 0:
                    satilacak_ev = oyuncu.sahip_olunan_evler[secim_sat - 1]
                    if False in satilacak_ev.eksiklikler.values():
                        if not HIZLI_MOD:
                            print("Bu evi satamazsın! Önce tüm eksiklikleri tamir etmelisin.")
                    else:
                        oyuncu.para += satilacak_ev.satis_fiyati
                        oyuncu.sahip_olunan_evler.pop(secim_sat - 1)
                        if not HIZLI_MOD:
                            print(f"{satilacak_ev.tip} satıldı ve {satilacak_ev.satis_fiyati} TL kazandın!")
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")

    input("\nDevam etmek için Enter'a bas...")
    return 120


def ulasim_yap(oyuncu, zaman, trafik, otomasyon_modu=False, hedef_konum_adi=None):
    """Farklı konumlar arasında dinamik trafik yoğunluğuna göre seyahat etme eylemi."""
    if not HIZLI_MOD:
        print("\n--- ULAŞIM ---")
    diger_konumlar = [k for k, v in KONUMLAR.items() if v.ad != oyuncu.mevcut_konum.ad]

    yogunluk_katsayisi = trafik.get_yogunluk_katsayisi(zaman.saat)
    if not HIZLI_MOD:
        print(f"Anlık Trafik Yoğunluğu: {yogunluk_katsayisi:.2f}x Gecikme")

    # Temel seyahat süreleri ve maliyetleri
    ulasim_secenekleri = {
        "Otobüs": {"temel_sure": 45, "temel_maliyet": 10},
        "Taksi": {"temel_sure": 20, "temel_maliyet": 50}
    }

    try:
        if hedef_konum_adi is None:
             hedef_secim_str = input(f"Nereye gitmek istersin? (1-{len(diger_konumlar)}): ")
             if not hedef_secim_str: return 10
             hedef_secim = int(hedef_secim_str)
             hedef_konum_adi = diger_konumlar[hedef_secim - 1]

        if otomasyon_modu or hedef_konum_adi:
            arac_secim = "1" # Otomasyon veya AI her zaman en ucuzunu seçer
        else:
            if not HIZLI_MOD:
                print("\nNasıl seyahat etmek istersin?")
            for i, (arac, detay) in enumerate(ulasim_secenekleri.items()):
                tahmini_sure = int(detay["temel_sure"] * yogunluk_katsayisi)
                tahmini_maliyet = int(detay["temel_maliyet"] * (1 + (yogunluk_katsayisi - 1) / 2)) # Taksi ücreti de artar
                if not HIZLI_MOD:
                    print(f"{i+1}: {arac} (Süre: ~{tahmini_sure} dk, Maliyet: {tahmini_maliyet} TL)")
            arac_secim = input("Seçimin: ")

        secilen_arac_adi = list(ulasim_secenekleri.keys())[int(arac_secim) - 1]
        secilen_arac = ulasim_secenekleri[secilen_arac_adi]

        maliyet = int(secilen_arac["temel_maliyet"] * (1 + (yogunluk_katsayisi - 1) / 2))
        sure = int(secilen_arac["temel_sure"] * yogunluk_katsayisi)

        if oyuncu.para >= maliyet:
            oyuncu.para -= maliyet
            oyuncu.mevcut_konum = KONUMLAR[hedef_konum_adi]
            if not HIZLI_MOD:
                print(f"{hedef_konum_adi}'a {secilen_arac_adi} ile seyahat ettin. Süre: {sure} dakika, Maliyet: {maliyet} TL.")
            return sure
        else:
            if not HIZLI_MOD:
                print("Seyahat için yeterli paran yok.")
            return 10

    except (ValueError, IndexError):
        if not HIZLI_MOD:
            print("Geçersiz seçim.")
        return 10


def eylem_sec(oyuncu, zaman, piyasa, trafik):
    """Oyuncunun eylem seçmesini sağlar ve sonucu uygular."""
    if not HIZLI_MOD:
        print("\nNe yapmak istersin?")

    mumkun_eylemler = {
        "İşe Git": calis,
        "İş Piyasası": is_piyasasi,
        "Uyu": uyu,
        "Eğlen": eglen,
        "Eğitim Al (Okul/Üniversite)": okula_git,
        "Spor Yap": spor_yap,
        "Alışveriş Yap": alisveris_yap,
        "Kitap Oku": kitap_oku,
        "Envanteri Kullan": envanter_kullan,
        "Yatırım Yap": yatirim_yap,
        "İş Kur / Yönet": lambda o, z, p, t: is_kur(o) if o.isletme is None else isletmeyi_yonet(o, p),
        "Ticaret Yap": ticaret_yap,
        "Gazete Oku": gazete_oku,
        "Emlakçıya Git": emlakciya_git,
        "Sosyal Etkileşime Gir": sosyal_etkilesim,
        "Hastaneye Git": hastaneye_git,
        "Otomasyon Modunu Değiştir": None, # Özel durum
        "Ulaşım": ulasim_yap
    }

    gosterilecek_eylemler = []
    # Konuma özel eylemleri ekle
    for eylem_adi in oyuncu.mevcut_konum.mumkun_eylemler:
        if eylem_adi == "İşe Git":
            if oyuncu.is_durumu["kariyer"]: gosterilecek_eylemler.append("İşe Git")
        elif eylem_adi == "İş Piyasası":
             if not oyuncu.is_durumu["kariyer"]: gosterilecek_eylemler.append("İş Piyasası")
        else:
            gosterilecek_eylemler.append(eylem_adi)

    # Her zaman mümkün olan genel eylemler
    gosterilecek_eylemler.extend(["Ulaşım", "Otomasyon Modunu Değiştir"])

    for i, eylem in enumerate(gosterilecek_eylemler):
        if not HIZLI_MOD:
            print(f"{i+1}: {eylem}")

    try:
        secim = int(input(f"Seçimin (1-{len(gosterilecek_eylemler)}): "))
        secilen_eylem_adi = gosterilecek_eylemler[secim - 1]

        if secilen_eylem_adi == "Otomasyon Modunu Değiştir":
            oyuncu.otomasyon_modu = not oyuncu.otomasyon_modu
            if not HIZLI_MOD:
                print(f"Otomasyon modu şimdi {'AÇIK' if oyuncu.otomasyon_modu else 'KAPALI'}.")
                time.sleep(2)
            return 10

        fonksiyon = mumkun_eylemler[secilen_eylem_adi]
        # Fonksiyonların ihtiyaç duyduğu argümanları dinamik olarak belirle
        if secilen_eylem_adi in ["Alışveriş Yap", "Ticaret Yap", "Yatırım Yap"]:
             return fonksiyon(oyuncu, zaman, piyasa)
        elif secilen_eylem_adi == "Ulaşım":
             return fonksiyon(oyuncu, zaman, trafik)
        elif secilen_eylem_adi == "İş Kur / Yönet":
             return fonksiyon(oyuncu, zaman, piyasa, trafik) # Lambda fonksiyonu
        else:
             return fonksiyon(oyuncu)

    except (ValueError, IndexError):
        if not HIZLI_MOD:
            print("Geçersiz seçim. 10 dakikan boşa geçti.")
            time.sleep(1)
        return 10

def otomasyonu_calistir(oyuncu, zaman, piyasa, trafik):
    """Otomasyon modu aktifken oyuncunun temel ihtiyaçlarını karşılar."""
    if not HIZLI_MOD:
        print("\n--- OTOMASYON DEVREDE ---")

    # Yüksek öncelikli acil durumlar
    if oyuncu.aclik > 80:
        if oyuncu.mevcut_konum.ad != "Şehir Merkezi":
            if not HIZLI_MOD:
                print("Otomasyon: Alışveriş yapmak için Şehir Merkezi'ne gidiliyor.")
            return ulasim_yap(oyuncu, zaman, trafik, otomasyon_modu=True)
        if not HIZLI_MOD:
            print("Otomasyon: Açlık kritik seviyede, yemek yeniyor.")
        yemekler = [y for y in oyuncu.envanter if "yemeği" in y or "abur cubur" in y]
        if yemekler:
            return envanter_kullan(oyuncu, override_secim=yemekler[0])
        else:
            if not HIZLI_MOD:
                print("Otomasyon: Yiyecek kalmamış, marketten alınıyor.")
            return alisveris_yap(oyuncu, zaman, piyasa, otomasyon_hedef="ev yemeği")

    if oyuncu.hijyen < 20:
        if oyuncu.mevcut_konum.ad != "Ev":
            if not HIZLI_MOD:
                print("Otomasyon: Duş almak için Eve gidiliyor.")
            return ulasim_yap(oyuncu, zaman, trafik, otomasyon_modu=True)
        if not HIZLI_MOD:
            print("Otomasyon: Hijyen düşük, duş alınıyor.")
        if "sabun" in oyuncu.envanter:
            return envanter_kullan(oyuncu, override_secim="sabun")
        else:
            if not HIZLI_MOD:
                print("Otomasyon: Sabun kalmamış, markete gidiliyor...")
            return ulasim_yap(oyuncu, zaman, trafik, otomasyon_modu=True) # Önce markete git

    # Enerji yönetimi ve çalışma
    if oyuncu.enerji < 40:
        if not HIZLI_MOD:
            print("Otomasyon: Enerji çalışmak için yetersiz, uyumak gerekiyor.")
        return uyu(oyuncu)
    else:
        # Temel ihtiyaçlar karşılandıysa ve enerji yeterliyse para kazan
        if not HIZLI_MOD:
            print("Otomasyon: Temel ihtiyaçlar yerinde ve enerji yeterli, çalışmaya gidiliyor.")
        return calis(oyuncu)


def alisveris_yap(oyuncu, zaman, piyasa, otomasyon_hedef=None):
    """Alışveriş yapma eylemi."""
    if otomasyon_hedef:
        secilen_esya_adi = otomasyon_hedef
    else:
        if not HIZLI_MOD:
            print("\n--- MAĞAZA ---")
        for i, (esya, detaylar) in enumerate(veri.MAGAZA_ESYALARI.items()):
            if not HIZLI_MOD:
                print(f"{i+1}: {esya.capitalize()} - {detaylar['fiyat']} TL")

        try:
            secim = int(input(f"Ne almak istersin? (1-{len(veri.MAGAZA_ESYALARI)}), çıkmak için 0): "))
            if secim == 0:
                return 60

            secilen_esya_adi = list(veri.MAGAZA_ESYALARI.keys())[secim - 1]
        except (ValueError, IndexError):
            if not HIZLI_MOD:
                print("Geçersiz seçim.")
                time.sleep(2)
            return 60

    if secilen_esya_adi in veri.MAGAZA_ESYALARI:
        secilen_esya = veri.MAGAZA_ESYALARI[secilen_esya_adi]

        if oyuncu.para >= secilen_esya['fiyat']:
            oyuncu.para -= secilen_esya['fiyat']
            if secilen_esya_adi == "gazete":
                import copy
                yeni_gazete = {"gun": zaman.gun, "fiyat_gecmisi": copy.deepcopy(piyasa.fiyat_gecmisi)}
                oyuncu.gazeteler.append(yeni_gazete)
                if not HIZLI_MOD:
                    print(f"Gün {zaman.gun} tarihli gazete satın aldın.")
            else:
                oyuncu.envanter.append(secilen_esya_adi)
                if not HIZLI_MOD:
                    print(f"{secilen_esya_adi.capitalize()} satın aldın.")
        else:
            if not HIZLI_MOD:
                print("Yeterli paran yok.")
    if not HIZLI_MOD:
        time.sleep(2)
    return 60

def kitap_oku(oyuncu, zaman, piyasa, *args, **kwargs):
    """Kitap okuma eylemi."""
    if "kitap" not in oyuncu.envanter:
        # Kitap yoksa, otomatik olarak satın almayı dene
        if not HIZLI_MOD:
            print("AI: Okuyacak kitap yok, marketten alınıyor...")
        return alisveris_yap(oyuncu, zaman, piyasa, otomasyon_hedef="kitap")

    if "kitap" in oyuncu.envanter:
        if not HIZLI_MOD:
            print("1 saat kitap okuyarak zekanı geliştirdin.")
        oyuncu.zeka = min(100, oyuncu.zeka + veri.MAGAZA_ESYALARI["kitap"]["deger"])
        oyuncu.enerji -= 5
        oyuncu.mutluluk += 5
        oyuncu.envanter.remove("kitap")
        if not HIZLI_MOD:
            time.sleep(2)
        return 60
    else:
        # Bu kısım yukarıdaki kontrol nedeniyle artık ulaşılamaz, ancak güvenlik için kalabilir.
        if not HIZLI_MOD:
            print("Okuyacak bir kitabın yok. 1 saatin boşa geçti.")
            time.sleep(2)
        return 60

def envanter_kullan(oyuncu, override_secim=None):
    """Envanterdeki bir eşyayı kullanma eylemi."""
    if not oyuncu.envanter:
        if not HIZLI_MOD:
            print("Envanterin boş. 1 saatin boşa geçti.")
            time.sleep(2)
        return 60

    if override_secim:
        secilen_esya_adi = override_secim
    else:
        if not HIZLI_MOD:
            print("\n--- ENVANTER ---")
        for i, esya in enumerate(oyuncu.envanter):
            if not HIZLI_MOD:
                print(f"{i+1}: {esya.capitalize()}")

        try:
            secim = int(input(f"Ne kullanmak istersin? (1-{len(oyuncu.envanter)}), çıkmak için 0): "))
            if secim == 0:
                return 60

            secilen_esya_adi = oyuncu.envanter[secim - 1]
        except (ValueError, IndexError):
            if not HIZLI_MOD:
                print("Geçersiz seçim.")
                time.sleep(2)
            return 60

    if secilen_esya_adi in oyuncu.envanter:
        esya_detay = veri.MAGAZA_ESYALARI[secilen_esya_adi]
        etki_alani = esya_detay.get('etki')
        if not etki_alani:
            if not HIZLI_MOD:
                print("Bu eşyanın bir etkisi yok.")
                time.sleep(2)
            return 60

        deger = esya_detay['deger']
        mevcut_deger = getattr(oyuncu, etki_alani)
        setattr(oyuncu, etki_alani, min(100, max(0, mevcut_deger + deger)))

        if "metabolizma_etkisi" in esya_detay:
            oyuncu.metabolizma_hizi = 1.0 + esya_detay["metabolizma_etkisi"]
            oyuncu.metabolizma_etki_suresi = 4 * 60 # 4 saat
            if not HIZLI_MOD:
                print(f"Yediğin yiyecek metabolizmanı etkiledi! Mevcut hız: {oyuncu.metabolizma_hizi}x")

        if not HIZLI_MOD:
            print(f"{secilen_esya_adi.capitalize()} kullandın. {etki_alani.capitalize()} {deger} değişti.")
        oyuncu.envanter.remove(secilen_esya_adi)

    if not HIZLI_MOD:
        time.sleep(2)
    return 60

def calis(oyuncu, *args, **kwargs):
    """İşe giderek para kazanma ve tecrübe edinme eylemi."""
    if oyuncu.hastalik:
        if not HIZLI_MOD:
            print(f"Hastayken işe gidemezsin! Önce iyileşmelisin.")
            time.sleep(2)
        return 60

    if oyuncu.isletme:
        if not HIZLI_MOD:
            print("Kendi işinin patronusun, 'İşletmeyi Yönet' seçeneğini kullan.")
            time.sleep(2)
        return 60

    if not oyuncu.is_durumu["kariyer"]:
        if not HIZLI_MOD:
            print("Bir işin yok! Önce İş Piyasasından bir iş bulmalısın.")
            time.sleep(2)
        return 60

    if oyuncu.enerji >= 50:
        saat = 8
        kariyer = oyuncu.is_durumu["kariyer"]
        seviye_bilgisi = kariyer.get_seviye_bilgisi(oyuncu.is_durumu["seviye"])

        gunluk_kazanc = seviye_bilgisi["maas"] * saat
        tecrube_kazanci = saat * 2

        if not HIZLI_MOD:
            print(f"İşe gittin. {saat} saat boyunca '{seviye_bilgisi['unvan']}' olarak çalıştın.")
            print(f"Bugünkü kazancın: {gunluk_kazanc} TL. Kazandığın tecrübe: {tecrube_kazanci}.")

        oyuncu.para += gunluk_kazanc
        oyuncu.enerji -= 50
        oyuncu.mutluluk -= 15
        oyuncu.is_durumu["tecrube"] += tecrube_kazanci

        # Terfi kontrolü
        sonraki_seviye = oyuncu.is_durumu["seviye"] + 1
        sonraki_seviye_bilgisi = kariyer.get_seviye_bilgisi(sonraki_seviye)
        if sonraki_seviye_bilgisi and oyuncu.is_durumu["tecrube"] >= sonraki_seviye_bilgisi["tecrube_gereksinimi"]:
            oyuncu.is_durumu["seviye"] = sonraki_seviye
            oyuncu.is_durumu["tecrube"] = 0 # Tecrübe sıfırlanır
            if not HIZLI_MOD:
                print(f"\nTEBRİKLER! Terfi ettin! Yeni unvanın: {sonraki_seviye_bilgisi['unvan']}.")

        if not HIZLI_MOD:
            time.sleep(3)
        return saat * 60
    else:
        if not HIZLI_MOD:
            print("İşe gidemeyecek kadar yorgunsun. 1 saatin boşa geçti.")
            time.sleep(2)
        return 60

def uyu(oyuncu, *args, **kwargs):
    """Uyuma eylemi. AI kontrolünde her zaman 8 saat uyur."""
    saat = 8
    if not HIZLI_MOD:
        print(f"{saat} saat uyudun.")
    oyuncu.enerji = min(100, oyuncu.enerji + saat * 8)
    if not HIZLI_MOD:
        time.sleep(2)
    return saat * 60

def eglen(oyuncu):
    """Eğlenme eylemi."""
    if oyuncu.para >= 30:
        if not HIZLI_MOD:
            print("Dışarı çıkıp 2 saat eğlendin, keyfin yerine geldi!")
        oyuncu.mutluluk = min(100, oyuncu.mutluluk + 20)
        oyuncu.enerji -= 10
        oyuncu.para -= 30
        oyuncu.sosyal_beceri += 5
        if not HIZLI_MOD:
            time.sleep(2)
        return 120
    else:
        if not HIZLI_MOD:
            print("Eğlenmek için yeterli paran yok. 1 saatin boşa geçti.")
            time.sleep(2)
        return 60

def okula_git(oyuncu, *args, **kwargs):
    """Okula gitme ve üniversite eğitimi alma eylemi."""
    UNIVERSITE_SURESI = 1460 # 4 oyun yılı
    ZEKA_GEREKSINIMI = 80

    if oyuncu.diploma:
        if not HIZLI_MOD:
            print("Zaten bir üniversite diploman var!")
            time.sleep(2)
        return 60

    if oyuncu.universite_gun_sayaci > 0:
        if oyuncu.enerji >= 30 and oyuncu.para >= 100:
            gun_ilerlemesi = 5
            if not HIZLI_MOD:
                print(f"Üniversiteye gidip {gun_ilerlemesi} gün boyunca ders çalıştın.")
            oyuncu.universite_gun_sayaci = max(0, oyuncu.universite_gun_sayaci - gun_ilerlemesi)
            oyuncu.enerji -= 30
            oyuncu.para -= 100
            oyuncu.mutluluk -= 15

            if oyuncu.universite_gun_sayaci == 0:
                oyuncu.diploma = True
                if not HIZLI_MOD:
                    print("\nTEBRİKLER! Üniversiteden başarıyla mezun oldun ve bir diploma kazandın!")
            else:
                if not HIZLI_MOD:
                    print(f"Mezuniyete kalan süre: {oyuncu.universite_gun_sayaci} gün.")

            if not HIZLI_MOD:
                time.sleep(2)
            return 8 * 60 # Üniversite günü 8 saat sürer
        else:
            if not HIZLI_MOD:
                print("Üniversiteye gidecek enerjin veya paran yok. 1 saatin boşa geçti.")
                time.sleep(2)
            return 60

    else: # Henüz üniversiteye başlamamış
        # AI her zaman temel okula gitmeyi seçer
        secim = '1'
        if secim == '1':
            if oyuncu.enerji >= 20 and oyuncu.para >= 50:
                if not HIZLI_MOD:
                    print("Okula gidip 4 saat ders çalıştın.")
                oyuncu.zeka = min(100, oyuncu.zeka + 5)
                oyuncu.enerji -= 20
                oyuncu.para -= 50
                oyuncu.mutluluk -= 10
                if not HIZLI_MOD:
                    time.sleep(2)
                return 4 * 60
            else:
                if not HIZLI_MOD:
                    print("Okula gidecek enerjin veya paran yok. 1 saatin boşa geçti.")
                    time.sleep(2)
                return 60
        elif secim == '2' and oyuncu.zeka >= ZEKA_GEREKSINIMI:
            if not HIZLI_MOD:
                print(f"Üniversiteye kaydoldun! {UNIVERSITE_SURESI} gün sürecek zorlu bir macera başlıyor.")
            oyuncu.universite_gun_sayaci = UNIVERSITE_SURESI
            if not HIZLI_MOD:
                time.sleep(3)
            return 120
        else:
            if not HIZLI_MOD:
                print("Geçersiz seçim. 1 saatin boşa geçti.")
                time.sleep(2)
            return 60

def spor_yap(oyuncu):
    """Spor yapma eylemi."""
    if oyuncu.enerji >= 25:
        if not HIZLI_MOD:
            print("1 saat spor yaptın, sağlığın ve enerjin arttı!")
        oyuncu.saglik = min(100, oyuncu.saglik + 5)
        oyuncu.enerji -= 25
        oyuncu.mutluluk += 10
        if not HIZLI_MOD:
            time.sleep(2)
        return 60
    else:
        if not HIZLI_MOD:
            print("Spor yapamayacak kadar yorgunsun. 1 saatin boşa geçti.")
            time.sleep(2)
        return 60

def yatirim_yap(oyuncu, piyasa, ai_kontrol=False):
    """Yatırım yapma eylemi. AI için otomasyon mantığı içerir."""
    if ai_kontrol:
        # AI, basit bir strateji izler: Varsa sat, yoksa ve para varsa al.
        if oyuncu.portfoy: # Satacak bir şey varsa
            secim = '2'
        elif oyuncu.para > 500: # Satacak bir şey yoksa ve parası yeterliyse
            secim = '1'
        else: # Hiçbir şey yapma
            return 60
    else:
        if not HIZLI_MOD:
            print("\n--- YATIRIM MERKEZİ ---")
            print("1: Varlık Al")
            print("2: Varlık Sat")
        secim = input("Ne yapmak istersin? (1-2), çıkmak için 0): ")

    if secim == '1':
        if not HIZLI_MOD and not ai_kontrol:
            print("\n--- PİYASA (ALIM) ---")
        for i, (varlik, detaylar) in enumerate(piyasa.yatirim_mallari.items()):
            if not HIZLI_MOD:
                print(f"{i+1}: {varlik.replace('_', ' ').title()} - {detaylar['fiyat']} TL")

        try:
            if ai_kontrol:
                varlik_secim = random.randint(1, len(piyasa.yatirim_mallari))
                secilen_varlik_adi = list(piyasa.yatirim_mallari.keys())[varlik_secim - 1]
                fiyat = piyasa.yatirim_mallari[secilen_varlik_adi]['fiyat']
                # Harcayabileceği maksimum para (toplam paranın %50'si)
                harcanabilir_para = oyuncu.para * 0.5
                adet = int(harcanabilir_para / fiyat)
                if adet == 0: return 60 # Alacak parası yoksa çık
            else:
                varlik_secim = int(input(f"Ne almak istersin? (1-{len(piyasa.yatirim_mallari)}): "))
                adet = int(input("Kaç adet almak istersin?: "))
                secilen_varlik_adi = list(piyasa.yatirim_mallari.keys())[varlik_secim - 1]
                fiyat = piyasa.yatirim_mallari[secilen_varlik_adi]['fiyat']

            toplam_tutar = fiyat * adet
            if oyuncu.para >= toplam_tutar:
                oyuncu.para -= toplam_tutar
                oyuncu.portfoy[secilen_varlik_adi] = oyuncu.portfoy.get(secilen_varlik_adi, 0) + adet
                if not HIZLI_MOD:
                    print(f"{adet} adet {secilen_varlik_adi.replace('_', ' ').title()} satın aldın.")
            elif not ai_kontrol:
                if not HIZLI_MOD:
                    print("Yeterli paran yok.")
        except (ValueError, IndexError):
            if not HIZLI_MOD:
                print("Geçersiz seçim.")

    elif secim == '2':
        if not oyuncu.portfoy:
            if not HIZLI_MOD:
                print("Satacak hiçbir varlığın yok.")
        else:
            if not HIZLI_MOD and not ai_kontrol:
                print("\n--- PORTFÖY (SATIM) ---")
            portfoy_listesi = list(oyuncu.portfoy.keys())
            for i, varlik in enumerate(portfoy_listesi):
                adet = oyuncu.portfoy[varlik]
                mevcut_fiyat = piyasa.yatirim_mallari[varlik]['fiyat']
                if not HIZLI_MOD and not ai_kontrol:
                    print(f"{i+1}: {varlik.replace('_', ' ').title()} ({adet} adet) - Mevcut Fiyat: {mevcut_fiyat} TL")

            try:
                if ai_kontrol:
                    varlik_secim = random.randint(1, len(portfoy_listesi))
                    secilen_varlik_adi = portfoy_listesi[varlik_secim - 1]
                    adet_satis = oyuncu.portfoy[secilen_varlik_adi] # Hepsini sat
                else:
                    varlik_secim = int(input(f"Ne satmak istersin? (1-{len(portfoy_listesi)}): "))
                    adet_satis = int(input("Kaç adet satmak istersin?: "))
                    secilen_varlik_adi = portfoy_listesi[varlik_secim - 1]

                if adet_satis > 0 and adet_satis <= oyuncu.portfoy.get(secilen_varlik_adi, 0):
                    fiyat = piyasa.yatirim_mallari[secilen_varlik_adi]['fiyat']
                    toplam_kazanc = fiyat * adet_satis
                    oyuncu.para += toplam_kazanc
                    oyuncu.portfoy[secilen_varlik_adi] -= adet_satis
                    if oyuncu.portfoy[secilen_varlik_adi] == 0:
                        del oyuncu.portfoy[secilen_varlik_adi]
                    if not HIZLI_MOD:
                        print(f"{adet_satis} adet {secilen_varlik_adi.replace('_', ' ').title()} sattın ve {toplam_kazanc} TL kazandın.")
                elif not ai_kontrol:
                    if not HIZLI_MOD:
                        print("Elinde o kadar varlık yok.")
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")

    if not HIZLI_MOD:
        time.sleep(2)
    return 120

def is_kur(oyuncu, *args, **kwargs):
    """Yeni bir iş kurma eylemi."""
    ai_kontrol = kwargs.get('ai_kontrol', False)
    kurulum_maliyeti = 2500
    if not HIZLI_MOD:
        print(f"\nKendi işini kurmak için gereken başlangıç sermayesi {kurulum_maliyeti} TL.")

    urun_tipi = None
    isletme_ismi = None

    if ai_kontrol:
        if oyuncu.para >= kurulum_maliyeti:
            # AI her zaman ilk ve en basit seçeneği seçer
            urun_tipi = list(veri.URUN_RECETELERI.keys())[0]
            isletme_ismi = f"{oyuncu.isim}'s Tech"
            if not HIZLI_MOD:
                print(f"AI, '{isletme_ismi}' adında bir şirket kurmaya karar verdi.")
        else:
            if not HIZLI_MOD:
                print("AI şirket kurmak istedi ama yeterli parası yok.")
            return 60 # Başarısız eylem için kısa süre
    else: # Manuel oyuncu
        if not HIZLI_MOD:
            print("Hangi alanda bir iş kurmak istersin?")
        urun_tipleri = list(veri.URUN_RECETELERI.keys())
        for i, urun in enumerate(urun_tipleri):
            if not HIZLI_MOD:
                print(f"{i+1}: {urun.capitalize()} Üretimi")
        try:
            secim = int(input(f"Seçimin (1-{len(urun_tipleri)}): "))
            urun_tipi = urun_tipleri[secim - 1]
            isletme_ismi = input("İşletmenin adı ne olsun?: ")
        except (ValueError, IndexError):
            if not HIZLI_MOD:
                print("Geçersiz seçim.")
                time.sleep(2)
            return 180

    if urun_tipi and isletme_ismi:
        if oyuncu.para >= kurulum_maliyeti:
            oyuncu.para -= kurulum_maliyeti
            oyuncu.isletme = Isletme(isletme_ismi, kurulum_maliyeti, urun_tipi, veri.DEPARTMANLAR, veri.URUN_RECETELERI)
            if not HIZLI_MOD:
                print(f"Tebrikler! '{isletme_ismi}' adında bir {urun_tipi} şirketi kurdun.")
        else:
            if not HIZLI_MOD:
                print("Yeterli paran yok.")

    if not HIZLI_MOD:
        time.sleep(2)
    return 180

def isletmeyi_yonet(oyuncu, piyasa, *args, **kwargs):
    """Mevcut işletmeyi yönetme eylemi."""
    ai_kontrol = kwargs.get('ai_kontrol', False)
    isletme = oyuncu.isletme
    if not HIZLI_MOD:
        print(f"\n--- {isletme.isim.upper()} YÖNETİM PANELİ ---")
        print(f"Sermaye: {isletme.sermaye} TL | Çalışanlar: {isletme.calisan_sayisi} | Müşteri Memnuniyeti: {isletme.musteri_memnuniyeti}% | Ar-Ge Seviyesi: {isletme.ar_ge_seviyesi}")

    if ai_kontrol:
        # AI, şimdilik en temel ve en önemli eylemi gerçekleştirir: Hammadde stoğunu kontrol et ve al.
        if not HIZLI_MOD:
            print("AI, işletme envanterini kontrol ediyor...")
        secim = '8' # Hammadde Satın Al
    else:
        hammadde_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in isletme.hammadde_envanteri.items() if v > 0])
        if not HIZLI_MOD:
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
        if not HIZLI_MOD:
            print("\n--- ÇALIŞAN LİSTESİ ---")
        for dep, calisan_listesi in isletme.departmanlar.items():
            if calisan_listesi:
                if not HIZLI_MOD:
                    print(f"\n-- {dep} Departmanı (Ort. Seviye: {isletme.get_ortalama_seviye(dep):.2f}) --")
                for calisan in calisan_listesi:
                    if not HIZLI_MOD:
                        print(f"  - {calisan.isim} (Seviye: {calisan.seviye}, Maaş: {calisan.maas}, Moral: {calisan.moral})")

    elif secim == '2':
        if not HIZLI_MOD:
            print("Hangi departmana alım yapmak istersin?")
        for i, dep in enumerate(veri.DEPARTMANLAR):
            if not HIZLI_MOD:
                print(f"{i+1}: {dep}")
        try:
            dep_secim = int(input(f"Seçimin (1-{len(veri.DEPARTMANLAR)}): "))
            adet = int(input("Kaç kişi işe almak istersin?: "))
            departman = veri.DEPARTMANLAR[dep_secim - 1]

            adaylar = []
            for _ in range(adet + 2): # Fazladan aday
                aday_ismi = f"{random.choice(veri.ISIM_LISTESI)} {random.choice(veri.SOYISIM_LISTESI)}"
                adaylar.append(Calisan(aday_ismi, departman, seviye=random.randint(1,5)))

            if not HIZLI_MOD:
                print("\n--- ADAY LİSTESİ ---")
            for i, aday in enumerate(adaylar):
                if not HIZLI_MOD:
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
                            if not HIZLI_MOD:
                                print(f"{adaylar[idx].isim}, {departman} departmanına katıldı.")
                        else:
                            if not HIZLI_MOD:
                                print(f"{adaylar[idx].isim} için yeterli sermaye yok.")
        except (ValueError, IndexError):
            if not HIZLI_MOD:
                print("Geçersiz seçim.")

    elif secim == '3':
        calisanlar = []
        for dep, calisan_listesi in isletme.departmanlar.items():
            for calisan in calisan_listesi:
                calisanlar.append((dep, calisan))

        if not calisanlar:
            if not HIZLI_MOD:
                print("Kovacak çalışan yok.")
        else:
            if not HIZLI_MOD:
                print("\n--- ÇALIŞAN KOV ---")
            for i, (dep, calisan) in enumerate(calisanlar):
                if not HIZLI_MOD:
                    print(f"{i+1}: {calisan.isim} ({dep}) - Seviye: {calisan.seviye}")

            try:
                secim_kov = int(input(f"Kimi kovmak istersin? (1-{len(calisanlar)}), çıkmak için 0): "))
                if secim_kov > 0:
                    dep, calisan_to_fire = calisanlar[secim_kov - 1]
                    isletme.departmanlar[dep].remove(calisan_to_fire)
                    if not HIZLI_MOD:
                        print(f"{calisan_to_fire.isim} işten çıkarıldı.")
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")

    elif secim == '4':
        if isletme.sermaye >= 1000:
            isletme.sermaye -= 1000
            for dep in isletme.departmanlar.values():
                for calisan in dep:
                    calisan.seviye += random.randint(1, 2)
            if not HIZLI_MOD:
                print("Tüm çalışanlara eğitim verildi, seviyeleri arttı.")
        else:
            if not HIZLI_MOD:
                print("Eğitim için işletmenin yeterli sermayesi yok.")

    elif secim == '5':
        if isletme.sermaye >= 750:
            isletme.sermaye -= 750
            for dep in isletme.departmanlar.values():
                for calisan in dep:
                    calisan.moral = min(100, calisan.moral + 15)
            if not HIZLI_MOD:
                print("Sosyal etkinlik düzenlendi, çalışanların morali yükseldi.")
        else:
            if not HIZLI_MOD:
                print("Etkinlik için işletmenin yeterli sermayesi yok.")

    elif secim == '6':
        try:
            miktar = int(input("Ne kadar sermaye eklemek istersin?: "))
            if oyuncu.para >= miktar:
                oyuncu.para -= miktar
                isletme.sermaye += miktar
                if not HIZLI_MOD:
                    print(f"İşletmeye {miktar} TL sermaye eklendi.")
            else:
                if not HIZLI_MOD:
                    print("Yeterli paran yok.")
        except ValueError:
            if not HIZLI_MOD:
                print("Geçersiz miktar.")

    elif secim == '7':
        if isletme.sermaye >= 300:
            isletme.sermaye -= 300
            isletme.musteri_memnuniyeti = min(100, isletme.musteri_memnuniyeti + 15)
            if not HIZLI_MOD:
                print("Pazarlama kampanyası müşteri memnuniyetini artırdı.")
        else:
            if not HIZLI_MOD:
                print("Pazarlama için işletmenin yeterli sermayesi yok.")

    elif secim == '8':
        if not HIZLI_MOD:
            print("\n--- HAMMADDE SATIN AL ---")
        if ai_kontrol:
             # AI, üretim için gerekli ilk hammaddeyi seçer
            recete = isletme.urun_receteleri.get(isletme.urun_tipi, {})
            if not recete:
                if not HIZLI_MOD:
                    print("AI: Ürün reçetesi bulunamadı.")
                return 60

            secilen_hammadde = list(recete.keys())[0]
            adet = 10 # Her seferinde sabit miktarda alır
            if not HIZLI_MOD:
                print(f"AI, {adet} adet {secilen_hammadde} almaya karar verdi.")
        else:
            hammadde_listesi = list(isletme.hammadde_envanteri.keys())
            for i, hammadde in enumerate(hammadde_listesi):
                fiyat = piyasa.ticari_mallar[hammadde]['fiyat']
                if not HIZLI_MOD:
                    print(f"{i+1}: {hammadde.capitalize()} - {fiyat} TL")
            try:
                secim_h = int(input(f"Ne almak istersin? (1-{len(hammadde_listesi)}): "))
                adet = int(input("Kaç adet almak istersin?: "))
                secilen_hammadde = hammadde_listesi[secim_h - 1]
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")
                    time.sleep(2)
                return 240

        fiyat = piyasa.ticari_mallar[secilen_hammadde]['fiyat']
        toplam_tutar = fiyat * adet

        if isletme.sermaye >= toplam_tutar:
            isletme.sermaye -= toplam_tutar
            isletme.hammadde_envanteri[secilen_hammadde] += adet
            if not HIZLI_MOD:
                print(f"{adet} adet {secilen_hammadde.capitalize()} satın alındı.")
        else:
            if not HIZLI_MOD:
                print("İşletmenin yeterli sermayesi yok.")

    elif secim == '9':
        maliyet = 2000 * isletme.ar_ge_seviyesi
        if not HIZLI_MOD:
            print(f"Mevcut Ar-Ge Seviyesi: {isletme.ar_ge_seviyesi}. Bir sonraki seviye için yatırım maliyeti: {maliyet} TL.")
        onay = input("Yatırım yapmak istiyor musun? (e/h): ").lower()
        if onay == 'e':
            if isletme.sermaye >= maliyet:
                isletme.sermaye -= maliyet
                isletme.ar_ge_seviyesi += 1
                if not HIZLI_MOD:
                    print(f"Ar-Ge yatırımı yapıldı! Yeni Ar-Ge Seviyesi: {isletme.ar_ge_seviyesi}.")
            else:
                if not HIZLI_MOD:
                    print("Yatırım için işletmenin yeterli sermayesi yok.")

    elif secim == '10':
        satis_degeri = isletme.sermaye # Basit hesaplama
        if not HIZLI_MOD:
            print(f"İşletmenin tahmini satış değeri: {satis_degeri} TL.")
        onay = input("İşletmeyi bu fiyata satmak istediğine emin misin? (e/h): ").lower()
        if onay == 'e':
            oyuncu.para += satis_degeri
            oyuncu.isletme = None
            if not HIZLI_MOD:
                print("İşletmeyi başarıyla sattın!")

    if not HIZLI_MOD:
        time.sleep(2)
    return 240

def ticaret_yap(oyuncu, piyasa):
    """Ticari mal alıp satma eylemi."""
    if not HIZLI_MOD:
        print("\n--- TİCARET MERKEZİ ---")
        print("1: Mal Al")
        print("2: Mal Sat")
    secim = input("Ne yapmak istersin? (1-2), çıkmak için 0): ")

    if secim == '0':
        return 60 # Eylem iptal edildi, 1 saat harcandı

    if secim == '1':
        if not HIZLI_MOD:
            print("\n--- PİYASA (ALIM) ---")
        mal_listesi = list(piyasa.ticari_mallar.keys())
        for i, (mal, detaylar) in enumerate(piyasa.ticari_mallar.items()):
            if not HIZLI_MOD:
                print(f"{i+1}: {mal.capitalize()} - {detaylar['fiyat']} TL")

        try:
            mal_secim_str = input(f"Ne almak istersin? (1-{len(mal_listesi)}): ")
            if not mal_secim_str: return 60
            mal_secim = int(mal_secim_str)

            adet_str = input("Kaç adet almak istersin?: ")
            if not adet_str: return 60
            adet = int(adet_str)

            if adet <= 0:
                if not HIZLI_MOD:
                    print("Geçersiz adet.")
                    time.sleep(2)
                return 120

            secilen_mal_adi = mal_listesi[mal_secim - 1]
            fiyat = piyasa.ticari_mallar[secilen_mal_adi]['fiyat']
            toplam_tutar = fiyat * adet

            if oyuncu.para >= toplam_tutar:
                oyuncu.para -= toplam_tutar
                oyuncu.ticari_envanter[secilen_mal_adi] = oyuncu.ticari_envanter.get(secilen_mal_adi, 0) + adet
                if not HIZLI_MOD:
                    print(f"{adet} adet {secilen_mal_adi.capitalize()} satın aldın.")
            else:
                if not HIZLI_MOD:
                    print("Yeterli paran yok.")
        except (ValueError, IndexError):
            if not HIZLI_MOD:
                print("Geçersiz seçim.")

    elif secim == '2':
        if not oyuncu.ticari_envanter:
            if not HIZLI_MOD:
                print("Satacak hiçbir ticari malın yok.")
        else:
            if not HIZLI_MOD:
                print("\n--- TİCARİ ENVANTER (SATIM) ---")
            envanter_listesi = list(oyuncu.ticari_envanter.keys())
            for i, mal in enumerate(envanter_listesi):
                adet = oyuncu.ticari_envanter[mal]
                mevcut_fiyat = piyasa.ticari_mallar[mal]['fiyat']
                if not HIZLI_MOD:
                    print(f"{i+1}: {mal.capitalize()} ({adet} adet) - Mevcut Fiyat: {mevcut_fiyat} TL")

            try:
                mal_secim_str = input(f"Ne satmak istersin? (1-{len(envanter_listesi)}): ")
                if not mal_secim_str: return 60
                mal_secim = int(mal_secim_str)

                adet_satis_str = input("Kaç adet satmak istersin?: ")
                if not adet_satis_str: return 60
                adet_satis = int(adet_satis_str)

                if adet_satis <= 0:
                    if not HIZLI_MOD:
                        print("Geçersiz adet.")
                        time.sleep(2)
                    return 120

                secilen_mal_adi = envanter_listesi[mal_secim - 1]

                if adet_satis <= oyuncu.ticari_envanter.get(secilen_mal_adi, 0):
                    fiyat = piyasa.ticari_mallar[secilen_mal_adi]['fiyat']
                    toplam_kazanc = fiyat * adet_satis
                    oyuncu.para += toplam_kazanc
                    oyuncu.ticari_envanter[secilen_mal_adi] -= adet_satis
                    if oyuncu.ticari_envanter[secilen_mal_adi] == 0:
                        del oyuncu.ticari_envanter[secilen_mal_adi]
                    if not HIZLI_MOD:
                        print(f"{adet_satis} adet {secilen_mal_adi.capitalize()} sattın ve {toplam_kazanc} TL kazandın.")
                else:
                    if not HIZLI_MOD:
                        print("Elinde o kadar mal yok.")
            except (ValueError, IndexError):
                if not HIZLI_MOD:
                    print("Geçersiz seçim.")
    else:
        if not HIZLI_MOD:
            print("Geçersiz seçim.")

    if not HIZLI_MOD:
        time.sleep(2)
    return 120

def gazete_oku(oyuncu):
    """Satın alınmış bir gazeteyi okuma eylemi."""
    if not oyuncu.gazeteler:
        if not HIZLI_MOD:
            print("Okuyacak hiç gazeten yok.")
            time.sleep(2)
        return 60

    if not HIZLI_MOD:
        print("\n--- GAZETELERİN ---")
    for i, gazete in enumerate(oyuncu.gazeteler):
        if not HIZLI_MOD:
            print(f"{i+1}: Gün {gazete['gun']} Tarihli Gazete")

    try:
        secim = int(input(f"Hangi gazeteyi okumak istersin? (1-{len(oyuncu.gazeteler)}), çıkmak için 0): "))
        if secim == 0:
            return 60

        secilen_gazete = oyuncu.gazeteler[secim - 1]
        if not HIZLI_MOD:
            print(f"\n--- GÜN {secilen_gazete['gun']} PİYASA BÜLTENİ ---")
        for mal, gecmis_veriler in secilen_gazete['fiyat_gecmisi'].items():
            if not HIZLI_MOD:
                print(f"\n--- {mal.capitalize()} ---")
            if not gecmis_veriler:
                if not HIZLI_MOD:
                    print("Veri yok.")
            else:
                for veri in gecmis_veriler:
                    if not HIZLI_MOD:
                        print(f"  Gün {veri['gun']}: {veri['fiyat']} TL")

        oyuncu.gazeteler.pop(secim - 1)
        if not HIZLI_MOD:
            print("\nGazeteyi okuduktan sonra attın.")

    except (ValueError, IndexError):
        if not HIZLI_MOD:
            print("Geçersiz seçim.")

    input("\nDevam etmek için Enter'a bas...")
    return 60

if __name__ == "__main__":
    main()
