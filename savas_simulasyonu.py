import pygame
import random
import sys
import numpy as np
import os
from nesneler.asker import YakinDovuscu, Menzilli, Asker
from ai_ajan import AIAjan

# --- Ayarlar ---
EKRAN_GENISLIK = 800
EKRAN_YUKSEKLIK = 600
FPS = 60
MAKSIMUM_BIRIM_SAYISI = 8 # Her takım için maksimum asker sayısı
GIRIS_BOYUTU = MAKSIMUM_BIRIM_SAYISI * 4 * 2 # (Birim Sayısı * Özellik Sayısı * Takım Sayısı)
EYLEM_SAYISI = 4 # 0: En Yakına Saldır, 1: En Zayıfa Saldır, 2: Toplu Saldır, 3: Dağıl

# --- Renkler ---
BEYAZ = (255, 255, 255)
KIRMIZI = (255, 0, 0)
MAVI = (0, 0, 255)
SIYAH = (0, 0, 0)

# --- Yardımcı Fonksiyonlar ---

def durumu_vektore_cevir(ordular, takim_id):
    """Oyun durumunu AI için sabit boyutlu bir numpy dizisine dönüştürür."""
    dost_takim = ordular[takim_id]
    dusman_takim_id = 2 if takim_id == 1 else 1
    dusman_takim = ordular[dusman_takim_id]

    vektor = np.zeros(GIRIS_BOYUTU)

    # Dost birimlerin bilgilerini ekle
    for i in range(MAKSIMUM_BIRIM_SAYISI):
        if i < len(dost_takim):
            asker = dost_takim[i]
            offset = i * 4
            vektor[offset] = asker.x / EKRAN_GENISLIK
            vektor[offset + 1] = asker.y / EKRAN_YUKSEKLIK
            vektor[offset + 2] = asker.hp / 100.0
            vektor[offset + 3] = 0 if isinstance(asker, YakinDovuscu) else 1

    # Düşman birimlerin bilgilerini ekle
    for i in range(MAKSIMUM_BIRIM_SAYISI):
        if i < len(dusman_takim):
            asker = dusman_takim[i]
            offset = (MAKSIMUM_BIRIM_SAYISI * 4) + (i * 4)
            vektor[offset] = asker.x / EKRAN_GENISLIK
            vektor[offset + 1] = asker.y / EKRAN_YUKSEKLIK
            vektor[offset + 2] = asker.hp / 100.0
            vektor[offset + 3] = 0 if isinstance(asker, YakinDovuscu) else 1

    return vektor

def en_yakin_dusman_bul(asker, dusman_ordusu):
    if not dusman_ordusu: return None
    return min(dusman_ordusu, key=lambda d: ((asker.x - d.x)**2 + (asker.y - d.y)**2))

def en_zayif_dusman_bul(dusman_ordusu):
    if not dusman_ordusu: return None
    return min(dusman_ordusu, key=lambda d: d.hp)

def eylemi_gerceklestir(takim_id, ordu, dusman_ordusu, eylem):
    """AI tarafından seçilen eylemi oyun içinde uygular."""
    if not ordu or not dusman_ordusu:
        return

    hedef = None
    if eylem == 0: # En Yakına Saldır
        for asker in ordu:
            hedef = en_yakin_dusman_bul(asker, dusman_ordusu)
            asker.hedef = hedef
        return
    elif eylem == 1: # En Zayıfa Saldır
        hedef = en_zayif_dusman_bul(dusman_ordusu)
    elif eylem == 2: # Toplu Saldır (en yakın düşmana odaklan)
        # Ordu merkezini bul
        merkez_x = sum(a.x for a in ordu) / len(ordu)
        merkez_y = sum(a.y for a in ordu) / len(ordu)
        sahte_asker = pygame.Rect(merkez_x, merkez_y, 1, 1)
        hedef = en_yakin_dusman_bul(sahte_asker, dusman_ordusu)
    elif eylem == 3: # Dağıl (rastgele pozisyonlara git)
        for asker in ordu:
            hedef_x = asker.x + random.randint(-50, 50)
            hedef_y = asker.y + random.randint(-50, 50)
            asker.hedef = pygame.Rect(hedef_x, hedef_y, 1, 1) # Hedef olarak sahte rect kullan
        return

    # Eylem 1 ve 2 için tüm birimlere aynı hedefi ata
    if hedef:
        for asker in ordu:
            asker.hedef = hedef

def odul_hesapla(ordu, dusman_ordusu, eski_hp, yeni_hp):
    """Eylemin sonucuna göre ödülü hesaplar."""
    odul = 0
    # Düşmana verilen hasar
    odul += (eski_hp['dusman'] - yeni_hp['dusman']) * 0.1
    # Alınan hasar
    odul -= (eski_hp['dost'] - yeni_hp['dost']) * 0.1
    return odul

def main():
    pygame.init()
    ekran = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
    pygame.display.set_caption("Yapay Zeka Savaş Simülatörü")
    saat = pygame.time.Clock()

    # AI Ajanlarını oluştur
    ajan1 = AIAjan(1, GIRIS_BOYUTU, EYLEM_SAYISI, "ogrenim_verileri/takim1_model.pth")
    ajan2 = AIAjan(2, GIRIS_BOYUTU, EYLEM_SAYISI, "ogrenim_verileri/takim2_model.pth")
    ajanlar = {1: ajan1, 2: ajan2}

    # Oyun Döngüsü Değişkenleri
    calisiyor = True
    dongu_sayaci = 0
    karar_verme_araligi = 30 # Her 30 frame'de bir karar ver

    # --- Yeni Oyun Başlatma ---
    ordular = { 1: [], 2: [] }
    mermiler = []

    # Ordu 1 (Mavi)
    for _ in range(5): ordular[1].append(YakinDovuscu(random.randint(50, 200), random.randint(50, 550), 1, MAVI))
    for _ in range(3): ordular[1].append(Menzilli(random.randint(50, 200), random.randint(50, 550), 1, MAVI))
    # Ordu 2 (Kırmızı)
    for _ in range(5): ordular[2].append(YakinDovuscu(random.randint(600, 750), random.randint(50, 550), 2, KIRMIZI))
    for _ in range(3): ordular[2].append(Menzilli(random.randint(600, 750), random.randint(50, 550), 2, KIRMIZI))

    eski_durumlar = {}
    secilen_eylemler = {}
    eski_hpler = {}

    while calisiyor:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False

        # --- AI Karar Verme Bloğu ---
        if dongu_sayaci % karar_verme_araligi == 0:
            for takim_id in ordular.keys():
                dusman_takim_id = 2 if takim_id == 1 else 1
                if ordular[takim_id] and ordular[dusman_takim_id]: # Eğer iki takımda da asker varsa
                    # 1. Mevcut durumu ve HP'leri kaydet
                    eski_durumlar[takim_id] = durumu_vektore_cevir(ordular, takim_id)
                    eski_hpler[takim_id] = {
                        'dost': sum(a.hp for a in ordular[takim_id]),
                        'dusman': sum(a.hp for a in ordular[dusman_takim_id])
                    }
                    # 2. Ajan'dan eylem seçmesini iste
                    eylem = ajanlar[takim_id].eylem_sec(eski_durumlar[takim_id])
                    secilen_eylemler[takim_id] = eylem
                    # 3. Eylemi uygula (hedef ata)
                    eylemi_gerceklestir(takim_id, ordular[takim_id], ordular[dusman_takim_id], eylem)

        # --- Oyun Mantığı Güncellemesi ---
        for takim_id, ordu in ordular.items():
            for asker in ordu:
                if hasattr(asker, 'hedef') and asker.hedef:
                    # Hedefin bir Asker nesnesi olup olmadığını ve canının olup olmadığını kontrol et
                    if isinstance(asker.hedef, Asker) and asker.hedef.hp <= 0:
                        asker.hedef = None
                        continue

                    saldiri_gerceklesti = False
                    # Sadece hedef bir Asker ise saldırı yap
                    if isinstance(asker.hedef, Asker):
                        if isinstance(asker, YakinDovuscu):
                            saldiri_gerceklesti = asker.saldir(asker.hedef)
                        elif isinstance(asker, Menzilli):
                            saldiri_gerceklesti = asker.saldir(asker.hedef, mermiler)

                    # Saldırmadıysa veya hedef bir konum ise hareket et
                    if not saldiri_gerceklesti:
                        asker.hareket_et(asker.hedef.x, asker.hedef.y)

        # Mermileri yönet
        for mermi in mermiler[:]:
            mermi.hareket_et()
            dusman_takim_id = 2 if mermi.takim_id == 1 else 1
            carpisma_oldu = False
            for dusman in ordular[dusman_takim_id]:
                if mermi.rect.colliderect(dusman.rect):
                    dusman.hp -= mermi.guc
                    mermiler.remove(mermi)
                    carpisma_oldu = True
                    break
            if not carpisma_oldu and (mermi.x < 0 or mermi.x > EKRAN_GENISLIK or mermi.y < 0 or mermi.y > EKRAN_YUKSEKLIK):
                mermiler.remove(mermi)

        # Ölen askerleri kaldır
        for ordu in ordular.values():
            for asker in ordu[:]:
                if asker.hp <= 0:
                    ordu.remove(asker)

        # --- AI Öğrenme Bloğu ---
        if dongu_sayaci > 0 and (dongu_sayaci + 1) % karar_verme_araligi == 0:
            for takim_id in ordular.keys():
                dusman_takim_id = 2 if takim_id == 1 else 1
                if eski_durumlar.get(takim_id) is not None:
                    yeni_durum = durumu_vektore_cevir(ordular, takim_id)
                    yeni_hpler = {
                        'dost': sum(a.hp for a in ordular[takim_id]),
                        'dusman': sum(a.hp for a in ordular[dusman_takim_id])
                    }
                    odul = odul_hesapla(ordular[takim_id], ordular[dusman_takim_id], eski_hpler[takim_id], yeni_hpler)
                    bitti = not ordular[takim_id] or not ordular[dusman_takim_id]

                    ajanlar[takim_id].hatirla(eski_durumlar[takim_id], secilen_eylemler[takim_id], odul, yeni_durum, bitti)
                    ajanlar[takim_id].ogren()

                    eski_durumlar[takim_id] = None # Bir sonraki karar anı için temizle

        # --- Çizim ---
        ekran.fill(SIYAH)
        for ordu in ordular.values():
            for asker in ordu:
                asker.ciz(ekran)
        for mermi in mermiler:
            mermi.ciz(ekran)
        pygame.display.flip()
        saat.tick(FPS)
        dongu_sayaci += 1

        # --- Kazanma Koşulu ---
        if not ordular[1] or not ordular[2]:
            kazanan = 0
            if not ordular[1]: kazanan = 2
            if not ordular[2]: kazanan = 1

            print(f"Oyun Bitti! Kazanan: Takım {kazanan}")

            # Son ödülleri ver ve öğren
            for takim_id in ajanlar.keys():
                if eski_durumlar.get(takim_id) is not None:
                    son_odul = 100 if takim_id == kazanan else -100
                    yeni_durum = durumu_vektore_cevir(ordular, takim_id)
                    ajanlar[takim_id].hatirla(eski_durumlar[takim_id], secilen_eylemler[takim_id], son_odul, yeni_durum, True)
                    ajanlar[takim_id].ogren()

            # Modelleri kaydet
            ajan1.modeli_kaydet()
            ajan2.modeli_kaydet()
            calisiyor = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
