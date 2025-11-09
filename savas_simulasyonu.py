import pygame
import random
import sys
import numpy as np
import os
import json
from nesneler.asker import YakinDovuscu, Menzilli, Asker
from ai_ajan import AIAjan

# --- Global Ayarlar ---
# Bu ayarlar `oyunu_oyna` fonksiyonuna parametre olarak geçilecek.
# Bu sayede turnuva modu farklı ayarlarla çalıştırılabilir.

# --- Renkler ---
RENKLER = {
    "BEYAZ": (255, 255, 255),
    "KIRMIZI": (255, 0, 0),
    "MAVI": (0, 0, 255),
    "SIYAH": (0, 0, 0)
}

# --- Yardımcı Fonksiyonlar (Değişiklik Yok) ---

def durumu_vektore_cevir(ordular, takim_id, maks_birim_sayisi, genislik, yukseklik):
    """Oyun durumunu AI için sabit boyutlu bir numpy dizisine dönüştürür."""
    dost_takim = ordular[takim_id]
    dusman_takim_id = 2 if takim_id == 1 else 1
    dusman_takim = ordular[dusman_takim_id]

    giris_boyutu = maks_birim_sayisi * 4 * 2
    vektor = np.zeros(giris_boyutu)

    for i in range(maks_birim_sayisi):
        if i < len(dost_takim):
            asker = dost_takim[i]
            offset = i * 4
            vektor[offset] = asker.x / genislik
            vektor[offset + 1] = asker.y / yukseklik
            vektor[offset + 2] = asker.hp / 100.0
            vektor[offset + 3] = 0 if isinstance(asker, YakinDovuscu) else 1

    for i in range(maks_birim_sayisi):
        if i < len(dusman_takim):
            asker = dusman_takim[i]
            offset = (maks_birim_sayisi * 4) + (i * 4)
            vektor[offset] = asker.x / genislik
            vektor[offset + 1] = asker.y / yukseklik
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
    if not ordu or not dusman_ordusu: return
    hedef = None
    if eylem == 0:
        for asker in ordu: asker.hedef = en_yakin_dusman_bul(asker, dusman_ordusu)
        return
    elif eylem == 1: hedef = en_zayif_dusman_bul(dusman_ordusu)
    elif eylem == 2:
        merkez_x = sum(a.x for a in ordu) / len(ordu)
        merkez_y = sum(a.y for a in ordu) / len(ordu)
        hedef = en_yakin_dusman_bul(pygame.Rect(merkez_x, merkez_y, 1, 1), dusman_ordusu)
    elif eylem == 3:
        for asker in ordu:
            hedef_x, hedef_y = asker.x + random.randint(-50, 50), asker.y + random.randint(-50, 50)
            asker.hedef = pygame.Rect(hedef_x, hedef_y, 1, 1)
        return
    if hedef:
        for asker in ordu: asker.hedef = hedef

def odul_hesapla(eski_hp, yeni_hp):
    odul = (eski_hp['dusman'] - yeni_hp['dusman']) * 0.1
    odul -= (eski_hp['dost'] - yeni_hp['dost']) * 0.1
    return odul

# --- Ana Oyun Fonksiyonu (Yeniden Düzenlendi) ---

def oyunu_oyna(ayarlar, gorsel_mod=True):
    """
    Simülasyonun bir tam maçını çalıştırır.
    :param ayarlar: Simülasyon yapılandırmasını içeren dictionary.
    :param gorsel_mod: Pygame penceresinin açılıp açılmayacağını belirler.
    :return: Kazanan takımın ID'si (1 veya 2), ya da 0 (hata/berabere).
    """
    sim_ayarlari = ayarlar['simulasyon']
    ekran_genislik = sim_ayarlari['ekran_genislik']
    ekran_yukseklik = sim_ayarlari['ekran_yukseklik']
    fps = sim_ayarlari['fps']
    maks_birim_sayisi = sim_ayarlari['maksimum_birim_sayisi']
    karar_verme_araligi = sim_ayarlari['karar_verme_araligi']
    giris_boyutu = maks_birim_sayisi * 4 * 2
    eylem_sayisi = 4

    ekran, saat = None, None
    if gorsel_mod:
        pygame.init()
        ekran = pygame.display.set_mode((ekran_genislik, ekran_yukseklik))
        pygame.display.set_caption("Yapay Zeka Savaş Simülatörü")
        saat = pygame.time.Clock()

    # AI Ajanlarını ve Orduları Ayarlardan Yükle
    takim1_ayarlari = ayarlar['takim1']
    takim2_ayarlari = ayarlar['takim2']
    ajan1 = AIAjan(1, giris_boyutu, eylem_sayisi, takim1_ayarlari['model'])
    ajan2 = AIAjan(2, giris_boyutu, eylem_sayisi, takim2_ayarlari['model'])
    ajanlar = {1: ajan1, 2: ajan2}

    ordular = {1: [], 2: []}
    mermiler = []

    renk1 = RENKLER[takim1_ayarlari['renk']]
    for _ in range(takim1_ayarlari['ordu']['YakinDovuscu']): ordular[1].append(YakinDovuscu(random.randint(50, 200), random.randint(50, 550), 1, renk1))
    for _ in range(takim1_ayarlari['ordu']['Menzilli']): ordular[1].append(Menzilli(random.randint(50, 200), random.randint(50, 550), 1, renk1))

    renk2 = RENKLER[takim2_ayarlari['renk']]
    for _ in range(takim2_ayarlari['ordu']['YakinDovuscu']): ordular[2].append(YakinDovuscu(random.randint(600, 750), random.randint(50, 550), 2, renk2))
    for _ in range(takim2_ayarlari['ordu']['Menzilli']): ordular[2].append(Menzilli(random.randint(600, 750), random.randint(50, 550), 2, renk2))

    calisiyor = True
    dongu_sayaci = 0
    eski_durumlar, secilen_eylemler, eski_hpler = {}, {}, {}

    while calisiyor:
        if gorsel_mod:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calisiyor = False

        # AI Karar Verme
        if dongu_sayaci % karar_verme_araligi == 0:
            for takim_id in ordular.keys():
                dusman_takim_id = 2 if takim_id == 1 else 1
                if ordular[takim_id] and ordular[dusman_takim_id]:
                    eski_durumlar[takim_id] = durumu_vektore_cevir(ordular, takim_id, maks_birim_sayisi, ekran_genislik, ekran_yukseklik)
                    eski_hpler[takim_id] = {'dost': sum(a.hp for a in ordular[takim_id]), 'dusman': sum(a.hp for a in ordular[dusman_takim_id])}
                    eylem = ajanlar[takim_id].eylem_sec(eski_durumlar[takim_id])
                    secilen_eylemler[takim_id] = eylem
                    eylemi_gerceklestir(takim_id, ordular[takim_id], ordular[dusman_takim_id], eylem)

        # Oyun Mantığı
        for ordu in ordular.values():
            for asker in ordu:
                if hasattr(asker, 'hedef') and asker.hedef:
                    if isinstance(asker.hedef, Asker) and asker.hedef.hp <= 0: asker.hedef = None
                    saldiri = False
                    if isinstance(asker.hedef, Asker):
                        if isinstance(asker, YakinDovuscu): saldiri = asker.saldir(asker.hedef)
                        elif isinstance(asker, Menzilli): saldiri = asker.saldir(asker.hedef, mermiler)
                    if not saldiri and asker.hedef: asker.hareket_et(asker.hedef.x, asker.hedef.y)

        for mermi in mermiler[:]:
            mermi.hareket_et()
            dusman_takim_id = 2 if mermi.takim_id == 1 else 1
            carpisma = False
            for dusman in ordular[dusman_takim_id]:
                if mermi.rect.colliderect(dusman.rect):
                    dusman.hp -= mermi.guc
                    mermiler.remove(mermi)
                    carpisma = True
                    break
            if not carpisma and not (0 < mermi.x < ekran_genislik and 0 < mermi.y < ekran_yukseklik):
                mermiler.remove(mermi)

        for ordu in ordular.values():
            ordu[:] = [asker for asker in ordu if asker.hp > 0]

        # AI Öğrenme
        if dongu_sayaci > 0 and (dongu_sayaci + 1) % karar_verme_araligi == 0:
            for takim_id in ordular.keys():
                if eski_durumlar.get(takim_id) is not None:
                    yeni_durum = durumu_vektore_cevir(ordular, takim_id, maks_birim_sayisi, ekran_genislik, ekran_yukseklik)
                    yeni_hpler = {'dost': sum(a.hp for a in ordular.get(takim_id, [])), 'dusman': sum(a.hp for a in ordular.get(2 if takim_id == 1 else 1, []))}
                    odul = odul_hesapla(eski_hpler[takim_id], yeni_hpler)
                    bitti = not ordular[1] or not ordular[2]
                    ajanlar[takim_id].hatirla(eski_durumlar[takim_id], secilen_eylemler[takim_id], odul, yeni_durum, bitti)
                    ajanlar[takim_id].ogren()
                    eski_durumlar[takim_id] = None

        # Çizim
        if gorsel_mod:
            ekran.fill(RENKLER["SIYAH"])
            for ordu in ordular.values():
                for asker in ordu: asker.ciz(ekran)
            for mermi in mermiler: mermi.ciz(ekran)
            pygame.display.flip()
            saat.tick(fps)

        dongu_sayaci += 1

        # Kazanma Koşulu
        if not ordular[1] or not ordular[2]:
            kazanan = 2 if not ordular[1] else 1
            print(f"Oyun Bitti! Kazanan: Takım {kazanan}")

            for takim_id in ajanlar.keys():
                if eski_durumlar.get(takim_id) is not None:
                    son_odul = 100 if takim_id == kazanan else -100
                    yeni_durum = durumu_vektore_cevir(ordular, takim_id, maks_birim_sayisi, ekran_genislik, ekran_yukseklik)
                    ajanlar[takim_id].hatirla(eski_durumlar[takim_id], secilen_eylemler[takim_id], son_odul, yeni_durum, True)
                    ajanlar[takim_id].ogren()

            ajan1.modeli_kaydet()
            ajan2.modeli_kaydet()
            calisiyor = False

            if gorsel_mod:
                pygame.quit()
            return kazanan

    if gorsel_mod:
        pygame.quit()
    return 0 # Döngü bir şekilde biterse (hata vb.)

def main():
    """Ana fonksiyon, simülasyonu görsel modda başlatır."""
    with open('ayarlar.json', 'r') as f:
        ayarlar = json.load(f)
    oyunu_oyna(ayarlar, gorsel_mod=True)

if __name__ == "__main__":
    main()
