# -*- coding: utf-8 -*-

import numpy as np
import os
import random

# Eylem sabitleri
EYLEMLER = [
    "İşe Git", "İş Piyasası", "Uyu", "Eğlen", "Eğitim Al (Okul/Üniversite)",
    "Spor Yap", "Alışveriş Yap", "Kitap Oku", "Envanteri Kullan", "Yatırım Yap",
    "İş Kur / Yönet", "Ticaret Yap", "Gazete Oku", "Emlakçıya Git",
    "Sosyal Etkileşime Gir", "Hastaneye Git", "Ulaşım"
]

class YapayZeka:
    def __init__(self, giris_boyutu, eylem_sayisi):
        self.giris_boyutu = giris_boyutu
        self.eylem_sayisi = eylem_sayisi
        self.eylemler = EYLEMLER

        # Sinir ağı mimarisi
        self.gizli_katman_1_boyutu = 200
        self.gizli_katman_2_boyutu = 100
        self.gizli_katman_3_boyutu = 50

        # Ağırlıkları ve bias'ları rastgele başlat
        self.W1 = np.random.randn(self.giris_boyutu, self.gizli_katman_1_boyutu) * np.sqrt(2. / self.giris_boyutu)
        self.b1 = np.zeros((1, self.gizli_katman_1_boyutu))
        self.W2 = np.random.randn(self.gizli_katman_1_boyutu, self.gizli_katman_2_boyutu) * np.sqrt(2. / self.gizli_katman_1_boyutu)
        self.b2 = np.zeros((1, self.gizli_katman_2_boyutu))
        self.W3 = np.random.randn(self.gizli_katman_2_boyutu, self.gizli_katman_3_boyutu) * np.sqrt(2. / self.gizli_katman_2_boyutu)
        self.b3 = np.zeros((1, self.gizli_katman_3_boyutu))
        self.W4 = np.random.randn(self.gizli_katman_3_boyutu, self.eylem_sayisi) * np.sqrt(2. / self.gizli_katman_3_boyutu)
        self.b4 = np.zeros((1, self.eylem_sayisi))

        # Öğrenme parametreleri
        self.ogrenme_orani = 0.001
        self.gama = 0.99  # İndirgeme faktörü
        self.epsilon = 1.0  # Keşif oranı
        self.epsilon_min = 0.01
        self.epsilon_azalma = 0.9995 # Daha yavaş azalma

        # Hafıza (tecrübe tekrarı için)
        self.hafiza = []
        self.hafiza_kapasitesi = 10000

    def relu(self, x):
        return np.maximum(0, x)

    def relu_turev(self, x):
        return (x > 0).astype(float)

    def tahmin_et(self, durum, egitim=False):
        durum = np.array(durum).reshape(1, -1) if durum.ndim == 1 else durum

        z1 = np.dot(durum, self.W1) + self.b1
        a1 = self.relu(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        a2 = self.relu(z2)
        z3 = np.dot(a2, self.W3) + self.b3
        a3 = self.relu(z3)
        q_degerleri = np.dot(a3, self.W4) + self.b4

        if egitim:
            return q_degerleri, (durum, a1, a2, a3, z1, z2, z3)
        return q_degerleri

    def eylem_sec(self, durum, mumkun_eylemler_mask):
        if np.random.rand() <= self.epsilon:
            gecerli_eylemler = np.where(mumkun_eylemler_mask)[0]
            if len(gecerli_eylemler) > 0:
                return np.random.choice(gecerli_eylemler)
            else:
                return np.random.randint(self.eylem_sayisi) # Fallback

        q_degerleri = self.tahmin_et(durum)[0]
        gecersiz_eylemler_mask = ~mumkun_eylemler_mask
        q_degerleri[gecersiz_eylemler_mask] = -np.inf # Geçersiz eylemleri seçme

        return np.argmax(q_degerleri)

    def tecrubeyi_hatirla(self, durum, eylem, odul, yeni_durum, bitti):
        if len(self.hafiza) >= self.hafiza_kapasitesi:
            self.hafiza.pop(0)
        self.hafiza.append((durum, eylem, odul, yeni_durum, bitti))

    def ogren(self, parti_boyutu=64):
        if len(self.hafiza) < parti_boyutu:
            return

        parti = random.sample(self.hafiza, parti_boyutu)

        durumlar = np.array([deneyim[0] for deneyim in parti])
        eylemler = np.array([deneyim[1] for deneyim in parti])
        oduller = np.array([deneyim[2] for deneyim in parti])
        yeni_durumlar = np.array([deneyim[3] for deneyim in parti])
        bittiler = np.array([deneyim[4] for deneyim in parti])

        mevcut_q_degerleri, cache = self.tahmin_et(durumlar, egitim=True)
        gelecek_q_degerleri = self.tahmin_et(yeni_durumlar)

        hedef_q = np.copy(mevcut_q_degerleri)

        for i in range(parti_boyutu):
            if bittiler[i]:
                hedef_q[i, eylemler[i]] = oduller[i]
            else:
                hedef_q[i, eylemler[i]] = oduller[i] + self.gama * np.max(gelecek_q_degerleri[i])

        durum_cache, a1, a2, a3, z1, z2, z3 = cache

        hata = hedef_q - mevcut_q_degerleri

        dW4 = np.dot(a3.T, hata)
        db4 = np.sum(hata, axis=0, keepdims=True)

        hata_3 = np.dot(hata, self.W4.T) * self.relu_turev(z3)
        dW3 = np.dot(a2.T, hata_3)
        db3 = np.sum(hata_3, axis=0, keepdims=True)

        hata_2 = np.dot(hata_3, self.W3.T) * self.relu_turev(z2)
        dW2 = np.dot(a1.T, hata_2)
        db2 = np.sum(hata_2, axis=0, keepdims=True)

        hata_1 = np.dot(hata_2, self.W2.T) * self.relu_turev(z1)
        dW1 = np.dot(durum_cache.T, hata_1)
        db1 = np.sum(hata_1, axis=0, keepdims=True)

        # Gradyan Kırpma (Gradient Clipping)
        np.clip(dW4, -1, 1, out=dW4)
        np.clip(db4, -1, 1, out=db4)
        np.clip(dW3, -1, 1, out=dW3)
        np.clip(db3, -1, 1, out=db3)
        np.clip(dW2, -1, 1, out=dW2)
        np.clip(db2, -1, 1, out=db2)
        np.clip(dW1, -1, 1, out=dW1)
        np.clip(db1, -1, 1, out=db1)

        self.W1 += self.ogrenme_orani * dW1
        self.b1 += self.ogrenme_orani * db1
        self.W2 += self.ogrenme_orani * dW2
        self.b2 += self.ogrenme_orani * db2
        self.W3 += self.ogrenme_orani * dW3
        self.b3 += self.ogrenme_orani * db3
        self.W4 += self.ogrenme_orani * dW4
        self.b4 += self.ogrenme_orani * db4

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_azalma

    def tecrubeyi_kaydet(self, dosya_adi='ai_tecrube.npy'):
        agirliklar = {
            'W1': self.W1, 'b1': self.b1,
            'W2': self.W2, 'b2': self.b2,
            'W3': self.W3, 'b3': self.b3,
            'W4': self.W4, 'b4': self.b4,
            'epsilon': self.epsilon
        }
        np.save(dosya_adi, agirliklar)
        print("Yapay zeka tecrübesi kaydedildi.")

    def tecrubeyi_yukle(self, dosya_adi='ai_tecrube.npy'):
        if os.path.exists(dosya_adi):
            try:
                agirliklar = np.load(dosya_adi, allow_pickle=True).item()
                self.W1, self.b1 = agirliklar['W1'], agirliklar['b1']
                self.W2, self.b2 = agirliklar['W2'], agirliklar['b2']
                self.W3, self.b3 = agirliklar['W3'], agirliklar['b3']
                self.W4, self.b4 = agirliklar['W4'], agirliklar['b4']
                self.epsilon = agirliklar.get('epsilon', self.epsilon)
                print("Yapay zeka tecrübesi yüklendi.")
            except Exception as e:
                print(f"Tecrübe dosyası yüklenirken hata oluştu: {e}")
                print("Yeni bir başlangıç yapılıyor.")
        else:
            print("Kaydedilmiş tecrübe bulunamadı, yeni bir başlangıç yapılıyor.")


def odul_hesapla(oyuncu_onceki, oyuncu_sonraki, secilen_eylem_adi, harcanan_dakika):
    """
    Bir eylemin sonucuna göre ödül puanı hesaplar.
    """
    odul = 0

    # Hayatta kalma ödülü (zamanla orantılı küçük bir bonus)
    odul += harcanan_dakika * 0.001

    # Statlardaki genel değişimler için ödüller/cezalar
    odul += (oyuncu_sonraki.saglik - oyuncu_onceki.saglik) * 0.2
    odul += (oyuncu_sonraki.mutluluk - oyuncu_onceki.mutluluk) * 0.1
    odul -= (oyuncu_sonraki.aclik - oyuncu_onceki.aclik) * 0.3 # Açlığın artması kötü
    odul += (oyuncu_sonraki.enerji - oyuncu_onceki.enerji) * 0.2
    odul += (oyuncu_sonraki.hijyen - oyuncu_onceki.hijyen) * 0.1 # Hijyenin artması iyi

    # Parasal yetersizlikten kaynaklanan başarısız eylemler için ceza
    maliyetli_eylemler = [
        "Alışveriş Yap", "Eğlen", "Yatırım Yap", "Ticaret Yap", "Emlakçıya Git",
        "Hastaneye Git", "Sosyal Etkileşime Gir", "Ulaşım"
    ]
    # Bir eylemin maliyetli olup olmadığını ve paranın değişip değişmediğini kontrol et
    if secilen_eylem_adi in maliyetli_eylemler and oyuncu_sonraki.para == oyuncu_onceki.para and oyuncu_onceki.para > 0:
         # Eğer para zaten 0 değilse ve değişmediyse, eylem muhtemelen başarısız oldu
         odul -= 15

    # --- Özel durumlar için büyük ödüller ve cezalar ---

    # 1. Hayat kurtaran eylemler
    # Kritik derecede açken yemek yemek
    if secilen_eylem_adi == "Envanteri Kullan" and oyuncu_onceki.aclik > 70 and oyuncu_sonraki.aclik < oyuncu_onceki.aclik:
        odul += 40

    # Kritik derecede yorgunken uyumak
    if secilen_eylem_adi == "Uyu" and oyuncu_onceki.enerji < 20 and oyuncu_sonraki.enerji > oyuncu_onceki.enerji:
        odul += 30

    # Hastayken hastaneye gidip iyileşmek
    if secilen_eylem_adi == "Hastaneye Git" and oyuncu_onceki.hastalik and not oyuncu_sonraki.hastalik:
        odul += 40

    # 2. Mantıksız veya kötü kararlar için cezalar
    # Çok açken uyumak
    if secilen_eylem_adi == "Uyu" and oyuncu_onceki.aclik > 80:
        odul -= 30

    # Zaten dolu olan bir statı artırmaya çalışmak
    if secilen_eylem_adi == "Uyu" and oyuncu_onceki.enerji > 95:
        odul -= 10
    if secilen_eylem_adi == "Envanteri Kullan" and oyuncu_onceki.aclik < 10 and oyuncu_sonraki.aclik < oyuncu_onceki.aclik:
        odul -= 10 # Gereksiz yere yemek yedi

    # 3. Finansal krizde doğru kararı vermek
    if secilen_eylem_adi == "İşe Git" and oyuncu_onceki.aclik > 60 and oyuncu_onceki.para < 15:
        odul += 30

    # 4. Kritik statlarda bulunmak için genel durum cezası
    if oyuncu_sonraki.aclik > 80 or oyuncu_sonraki.enerji < 10:
        odul -= 25

    # 5. Ölüm için çok büyük ceza
    if oyuncu_sonraki.saglik <= 0:
        odul -= 500

    return odul

def durumu_al(oyuncu, zaman, piyasa):
    """Oyunun mevcut durumunu yapay zeka için bir vektöre dönüştürür."""
    # Durum vektörünü oluştururken normalizasyon yapmak önemlidir.
    # Değerleri kabaca 0-1 arasına getirmek ağın öğrenmesini kolaylaştırır.
    durum = [
        oyuncu.saglik / 100.0,
        oyuncu.mutluluk / 100.0,
        oyuncu.enerji / 100.0,
        oyuncu.aclik / 100.0,
        oyuncu.hijyen / 100.0,
        np.clip(oyuncu.para / 10000.0, 0, 10), # Parayı normalleştir ve patlamasını önle (max 100k)
        oyuncu.zeka / 100.0,
        oyuncu.sosyal_beceri / 100.0,
        1 if oyuncu.diploma else 0,
        1 if oyuncu.hastalik else 0,
        zaman.saat / 24.0,
        zaman.gun % 7 / 7.0, # Haftanın günü
        # Oyuncunun envanterindeki yiyecek sayısı
        sum(1 for esya in oyuncu.envanter if "yemeği" in esya or "abur cubur" in esya) / 5.0,
        # Konum bilgisi (one-hot encoding)
        1 if oyuncu.mevcut_konum.ad == "Ev" else 0,
        1 if oyuncu.mevcut_konum.ad == "Şehir Merkezi" else 0,
        1 if oyuncu.mevcut_konum.ad == "Sanayi Bölgesi" else 0,
    ]
    return np.array(durum)
