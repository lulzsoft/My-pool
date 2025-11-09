import pygame
import random
import sys
import numpy as np
import os
import json
from nesneler.asker import Isci, YakinDovuscu, Menzilli, Asker
from nesneler.bina import Bina, Kisla
from nesneler.kaynak import Kaynak
from ai_ajan import AIAjan

# --- Renkler ---
RENKLER = {"BEYAZ": (255, 255, 255), "KIRMIZI": (255, 0, 0), "MAVI": (0, 0, 255), "SIYAH": (0, 0, 0)}

# --- AI Strateji Tanımları ---
EYLEM_UZAYI = [
    "ISCI_URET", "KISLA_INSA_ET", "YAKIN_DOVUSCU_URET", "MENZILLI_URET",
    "ISCI_ODUNA_GONDER", "ISCI_GIDAYA_GONDER", "ISCI_MADENE_GONDER",
    "TOPLU_SALDIRI", "USSE_DON"
]
EYLEM_SAYISI = len(EYLEM_UZAYI)

def durumu_vektore_cevir_gelismis(yonetici, takim_id):
    """Oyun durumunu AI için gelişmiş bir vektöre dönüştürür."""
    dusman_takim_id = 2 if takim_id == 1 else 1

    # Kendi kaynak ve birim bilgileri
    dost_kaynaklar = yonetici.kaynaklar[f"takim{takim_id}"]
    dost_birimler = yonetici.birimler[takim_id]
    dost_binalar = yonetici.binalar[takim_id]

    # Düşman birim ve bina bilgileri (görüş alanı varsayımıyla)
    dusman_birimler = yonetici.birimler[dusman_takim_id]
    dusman_binalar = yonetici.binalar[dusman_takim_id]

    vektor = [
        # Kaynaklar (normalize edilebilir)
        dost_kaynaklar.get('odun', 0) / 1000.0,
        dost_kaynaklar.get('gıda', 0) / 1000.0,
        dost_kaynaklar.get('maden', 0) / 1000.0,

        # Birim sayıları
        sum(1 for b in dost_birimler if isinstance(b, Isci)) / 20.0,
        sum(1 for b in dost_birimler if isinstance(b, YakinDovuscu)) / 20.0,
        sum(1 for b in dost_birimler if isinstance(b, Menzilli)) / 20.0,

        # Bina sayıları
        sum(1 for b in dost_binalar if isinstance(b, Kisla)) / 5.0,

        # Düşman bilgileri (basit)
        len(dusman_birimler) / 40.0,
        len(dusman_binalar) / 10.0,
    ]

    # Vektörün geri kalanını doldur (sabit boyut için)
    # Gerekirse haritadaki kaynakların konumları gibi ek bilgiler eklenebilir.
    mevcut_boyut = len(vektor)
    hedef_boyut = yonetici.girdi_boyutu
    if mevcut_boyut < hedef_boyut:
        vektor.extend([0.0] * (hedef_boyut - mevcut_boyut))

    return np.array(vektor)

def eylemi_gerceklestir_stratejik(yonetici, takim_id, eylem_index):
    """AI tarafından seçilen stratejik eylemi oyunda uygular."""
    eylem = EYLEM_UZAYI[eylem_index]

    ana_bina = next((b for b in yonetici.binalar[takim_id] if isinstance(b, Bina) and not isinstance(b, Kisla)), None)
    isciler = [b for b in yonetici.birimler[takim_id] if isinstance(b, Isci)]
    bos_isci = next((i for i in isciler if i.gorev == "bos"), None)

    if eylem == "ISCI_URET" and ana_bina and yonetici.birim_uretebilir_mi(takim_id, "Isci"):
        # Ana binadan işçi üret (bu özellik Bina sınıfına eklenebilir)
        # Şimdilik direkt oluşturuyoruz
        yonetici.maliyeti_dus(takim_id, "Isci")
        renk = RENKLER[yonetici.ayarlar[f'takim{takim_id}']['renk']]
        yeni_isci = Isci(ana_bina.x + 20, ana_bina.y, takim_id, renk)
        yonetici.birimler[takim_id].append(yeni_isci)

    elif eylem == "KISLA_INSA_ET" and bos_isci and yonetici.birim_uretebilir_mi(takim_id, "Kisla"):
        # Rastgele bir konuma kışla inşa et
        yonetici.maliyeti_dus(takim_id, "Kisla")
        renk = RENKLER[yonetici.ayarlar[f'takim{takim_id}']['renk']]
        x = ana_bina.x + random.randint(-100, 100)
        y = ana_bina.y + random.randint(-100, 100)
        yeni_kisla = Kisla(x,y, takim_id, renk)
        yonetici.binalar[takim_id].append(yeni_kisla) # Şimdilik anında inşa

    elif eylem in ["YAKIN_DOVUSCU_URET", "MENZILLI_URET"]:
        kisla = next((b for b in yonetici.binalar[takim_id] if isinstance(b, Kisla)), None)
        birim_tipi = "YakinDovuscu" if eylem == "YAKIN_DOVUSCU_URET" else "Menzilli"
        if kisla and yonetici.birim_uretebilir_mi(takim_id, birim_tipi):
            yonetici.maliyeti_dus(takim_id, birim_tipi)
            kisla.birim_uret(birim_tipi)

    elif eylem.startswith("ISCI_") and bos_isci:
        kaynak_tipi = eylem.split('_')[1].lower()
        hedef_kaynak = yonetici.en_yakin_kaynagi_bul(bos_isci, kaynak_tipi)
        if hedef_kaynak:
            bos_isci.gorev_ata("topla", hedef_kaynak)

    elif eylem == "TOPLU_SALDIRI" and yonetici.savas_basladi_mi:
        savascilar = [b for b in yonetici.birimler[takim_id] if isinstance(b, (YakinDovuscu, Menzilli))]
        dusman_takim_id = 2 if takim_id == 1 else 1
        hedef = yonetici.en_yakin_dusman_birim_bul(savascilar, dusman_takim_id)
        if hedef:
            for savasci in savascilar:
                savasci.hedef = hedef

def odul_hesapla_gelismis(yonetici, takim_id, eski_durum_vektor, yeni_durum_vektor):
    """Stratejik eylemin sonucuna göre ödülü hesaplar."""
    odul = 0
    # Kaynak artışı
    odul += (yeni_durum_vektor[0] - eski_durum_vektor[0]) * 5 # Odun
    odul += (yeni_durum_vektor[1] - eski_durum_vektor[1]) * 5 # Gıda
    odul += (yeni_durum_vektor[2] - eski_durum_vektor[2]) * 8 # Maden

    # Birim ve bina artışı
    odul += (yeni_durum_vektor[3] - eski_durum_vektor[3]) * 10 # İşçi
    odul += (yeni_durum_vektor[4] - eski_durum_vektor[4]) * 20 # Savaşçı
    odul += (yeni_durum_vektor[6] - eski_durum_vektor[6]) * 30 # Kışla

    # Düşmana verilen hasar (dolaylı olarak düşman birim sayısının azalmasıyla ölçülür)
    odul += (eski_durum_vektor[7] - yeni_durum_vektor[7]) * 50

    return odul

class OyunYonetici:
    def __init__(self, ayarlar):
        self.ayarlar = ayarlar
        self.sim_ayarlari = ayarlar['simulasyon']
        self.ekonomi_ayarlari = ayarlar['ekonomi']

        self.saldirmazlik_suresi = self.sim_ayarlari.get('saldirmazlik_suresi', 0)
        self.oyun_dongusu = 0
        self.savas_basladi_mi = self.saldirmazlik_suresi <= 0

        self.girdi_boyutu = 20 # Sabit bir girdi boyutu belirliyoruz.
        self.ajanlar = {
            1: AIAjan(1, self.girdi_boyutu, EYLEM_SAYISI, ayarlar['takim1']['model']),
            2: AIAjan(2, self.girdi_boyutu, EYLEM_SAYISI, ayarlar['takim2']['model'])
        }

        self.kaynaklar = {"takim1": self.ekonomi_ayarlari['baslangic_kaynaklari'].copy(),
                          "takim2": self.ekonomi_ayarlari['baslangic_kaynaklari'].copy()}

        self.harita_kaynaklari = []
        self.binalar = {1: [], 2: []}
        self.birimler = {1: [], 2: []}
        self.mermiler = []
        self.haritayi_kur()
        self.baslangic_birimlerini_kur()

    def haritayi_kur(self):
        #... (öncekiyle aynı)
        genislik = self.sim_ayarlari['ekran_genislik']
        yukseklik = self.sim_ayarlari['ekran_yukseklik']
        for tip, sayi in self.ayarlar['harita']['kaynak_sayisi'].items():
            for _ in range(sayi):
                x = random.randint(50, genislik - 50)
                y = random.randint(50, yukseklik - 50)
                self.harita_kaynaklari.append(Kaynak(x, y, tip))

    def baslangic_birimlerini_kur(self):
        #... (öncekiyle aynı)
        takim1_ayarlari = self.ayarlar['takim1']
        renk1 = RENKLER[takim1_ayarlari['renk']]
        ana_bina1 = Bina(100, self.sim_ayarlari['ekran_yukseklik'] // 2, 1, renk1, can=5000)
        self.binalar[1].append(ana_bina1)
        for _ in range(takim1_ayarlari['baslangic_birimleri']['Isci']):
            self.birimler[1].append(Isci(ana_bina1.x + 70, ana_bina1.y + random.randint(-20, 20), 1, renk1))

        takim2_ayarlari = self.ayarlar['takim2']
        renk2 = RENKLER[takim2_ayarlari['renk']]
        ana_bina2 = Bina(self.sim_ayarlari['ekran_genislik'] - 100, self.sim_ayarlari['ekran_yukseklik'] // 2, 2, renk2, can=5000)
        self.binalar[2].append(ana_bina2)
        for _ in range(takim2_ayarlari['baslangic_birimleri']['Isci']):
            self.birimler[2].append(Isci(ana_bina2.x - 70, ana_bina2.y + random.randint(-20, 20), 2, renk2))

    def birim_uretebilir_mi(self, takim_id, birim_tipi):
        #... (öncekiyle aynı)
        maliyet = self.ekonomi_ayarlari['birim_maliyetleri'][birim_tipi]
        mevcut_kaynaklar = self.kaynaklar[f"takim{takim_id}"]
        for kaynak, deger in maliyet.items():
            if mevcut_kaynaklar.get(kaynak, 0) < deger:
                return False
        return True

    def maliyeti_dus(self, takim_id, birim_tipi):
        #... (öncekiyle aynı)
        maliyet = self.ekonomi_ayarlari['birim_maliyetleri'][birim_tipi]
        for kaynak, deger in maliyet.items():
            self.kaynaklar[f"takim{takim_id}"][kaynak] -= deger

    def en_yakin_kaynagi_bul(self, isci, kaynak_tipi):
        uygun_kaynaklar = [k for k in self.harita_kaynaklari if k.kaynak_tipi == kaynak_tipi and k.miktar > 0]
        if not uygun_kaynaklar: return None
        return min(uygun_kaynaklar, key=lambda k: isci.mesafe_hesapla(k))

    def en_yakin_dusman_birim_bul(self, savascilar, dusman_takim_id):
        if not self.birimler[dusman_takim_id] or not savascilar: return None
        # Basitlik için ilk savaşçının konumunu referans al
        return min(self.birimler[dusman_takim_id], key=lambda d: savascilar[0].mesafe_hesapla(d))

def oyunu_oyna(ayarlar, gorsel_mod=True):
    yonetici = OyunYonetici(ayarlar)
    sim_ayarlari = ayarlar['simulasyon']

    # ... (pygame başlatma kısmı öncekiyle aynı)
    ekran, saat, font = None, None, None
    if gorsel_mod:
        pygame.init()
        ekran = pygame.display.set_mode((sim_ayarlari['ekran_genislik'], sim_ayarlari['ekran_yukseklik']))
        pygame.display.set_caption("Stratejik AI RTS Simülatörü")
        saat = pygame.time.Clock()
        font = pygame.font.SysFont(None, 24)

    calisiyor = True
    dongu_sayaci = 0
    eski_durumlar = {}
    secilen_eylemler = {}

    while calisiyor:
        if gorsel_mod and pygame.event.get(pygame.QUIT): calisiyor = False

        # --- Saldırmazlık Süresi Kontrolü ---
        if not yonetici.savas_basladi_mi:
            yonetici.oyun_dongusu += 1
            if yonetici.oyun_dongusu >= yonetici.saldirmazlik_suresi:
                yonetici.savas_basladi_mi = True
                print("--- SAVAŞ BAŞLADI! ---")

        # --- AI Karar Verme Bloğu ---
        if dongu_sayaci % sim_ayarlari['karar_verme_araligi'] == 0:
            for takim_id in yonetici.ajanlar.keys():
                eski_durumlar[takim_id] = durumu_vektore_cevir_gelismis(yonetici, takim_id)
                eylem = yonetici.ajanlar[takim_id].eylem_sec(eski_durumlar[takim_id])
                secilen_eylemler[takim_id] = eylem
                eylemi_gerceklestir_stratejik(yonetici, takim_id, eylem)

        # --- Oyun Mantığı Güncellemesi ---
        # ... (öncekiyle büyük ölçüde aynı, sadece AI görev ataması kaldırıldı)
        for takim_id, birim_listesi in yonetici.birimler.items():
            ana_bina = next((b for b in yonetici.binalar[takim_id] if isinstance(b, Bina) and not isinstance(b, Kisla)), None)
            for birim in birim_listesi:
                if isinstance(birim, Isci):
                    sonuc = birim.guncelle(ana_bina)
                    if sonuc and sonuc[0] == 'kaynak_birak':
                        yonetici.kaynaklar[f"takim{takim_id}"][sonuc[1]] += sonuc[2]
                elif isinstance(birim, (YakinDovuscu, Menzilli)):
                     if birim.hedef and birim.hedef.hp > 0 and yonetici.savas_basladi_mi:
                         if isinstance(birim, YakinDovuscu): birim.saldir(birim.hedef)
                         elif isinstance(birim, Menzilli): birim.saldir(birim.hedef, yonetici.mermiler)
                         birim.hareket_et(birim.hedef.x, birim.hedef.y)
                     else: birim.hedef = None

        for takim_id, bina_listesi in yonetici.binalar.items():
            for bina in bina_listesi:
                if isinstance(bina, Kisla):
                    uretilen = bina.guncelle()
                    if uretilen:
                        renk = RENKLER[ayarlar[f'takim{takim_id}']['renk']]
                        yeni_asker = YakinDovuscu(bina.uretim_noktasi[0], bina.uretim_noktasi[1], takim_id, renk) if uretilen == "YakinDovuscu" else Menzilli(bina.uretim_noktasi[0], bina.uretim_noktasi[1], takim_id, renk)
                        yonetici.birimler[takim_id].append(yeni_asker)

        yonetici.harita_kaynaklari[:] = [k for k in yonetici.harita_kaynaklari if k.miktar > 0]
        for ordu in yonetici.birimler.values(): ordu[:] = [b for b in ordu if b.hp > 0]

        # --- AI Öğrenme Bloğu ---
        if dongu_sayaci > 0 and (dongu_sayaci + 1) % sim_ayarlari['karar_verme_araligi'] == 0:
            for takim_id in yonetici.ajanlar.keys():
                if eski_durumlar.get(takim_id) is not None:
                    yeni_durum = durumu_vektore_cevir_gelismis(yonetici, takim_id)
                    odul = odul_hesapla_gelismis(yonetici, takim_id, eski_durumlar[takim_id], yeni_durum)
                    bitti = not yonetici.binalar[1] or not yonetici.binalar[2]
                    yonetici.ajanlar[takim_id].hatirla(eski_durumlar[takim_id], secilen_eylemler[takim_id], odul, yeni_durum, bitti)
                    yonetici.ajanlar[takim_id].ogren()

        # --- Çizim ve Kazanma Koşulu --- (öncekiyle aynı)
        if gorsel_mod:
            ekran.fill(RENKLER["SIYAH"])
            for kaynak in yonetici.harita_kaynaklari: kaynak.ciz(ekran)
            for takim_list in yonetici.binalar.values():
                for bina in takim_list: bina.ciz(ekran)
            for takim_list in yonetici.birimler.values():
                for birim in takim_list: birim.ciz(ekran)
            kaynak_yazisi1 = f"Takim 1: {yonetici.kaynaklar['takim1']}"
            yazi_render1 = font.render(kaynak_yazisi1, True, RENKLER['BEYAZ'])
            ekran.blit(yazi_render1, (10, 10))
            kaynak_yazisi2 = f"Takim 2: {yonetici.kaynaklar['takim2']}"
            yazi_render2 = font.render(kaynak_yazisi2, True, RENKLER['BEYAZ'])
            ekran.blit(yazi_render2, (sim_ayarlari['ekran_genislik'] - yazi_render2.get_width() - 10, 10))
            pygame.display.flip()
            saat.tick(sim_ayarlari['fps'])

        dongu_sayaci += 1
        if not yonetici.binalar[1] or not yonetici.binalar[2]:
            kazanan = 2 if not yonetici.binalar[1] else 1
            print(f"Oyun Bitti! Kazanan: Takım {kazanan}")
            # Son ödülleri ver ve kaydet
            for takim_id in yonetici.ajanlar.keys():
                yonetici.ajanlar[takim_id].modeli_kaydet()
            calisiyor = False

    if gorsel_mod: pygame.quit()
    return kazanan if 'kazanan' in locals() else 0

def main():
    with open('ayarlar.json', 'r') as f:
        ayarlar = json.load(f)
    oyunu_oyna(ayarlar, gorsel_mod=True)

if __name__ == "__main__":
    main()
