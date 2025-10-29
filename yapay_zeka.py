# -*- coding: utf-8 -*-

import numpy as np

class YapayZeka:
    """
    Hayat simülasyonu için karakteri yöneten, Pekiştirmeli Öğrenme (Q-Learning benzeri)
    yöntemini kullanan bir sinir ağı modeli. Model, zamanla aldığı ödül ve cezalara
    göre kendini geliştirir.
    """
    def __init__(self, girdi_boyutu=6, gizli_katman_boyutu=100, cikti_boyutu=7):
        """
        Sinir ağını ve öğrenme parametrelerini başlatır.
        """
        # Katman boyutları
        self.girdi_boyutu = girdi_boyutu
        self.gizli_boyutu_1 = gizli_katman_boyutu
        self.gizli_boyutu_2 = gizli_katman_boyutu
        self.gizli_boyutu_3 = gizli_katman_boyutu
        self.cikti_boyutu = cikti_boyutu

        # Ağırlıkların ve sapmaların (bias) rastgele başlatılması
        self.W1 = np.random.randn(self.girdi_boyutu, self.gizli_boyutu_1) * 0.1
        self.b1 = np.zeros((1, self.gizli_boyutu_1))
        self.W2 = np.random.randn(self.gizli_boyutu_1, self.gizli_boyutu_2) * 0.1
        self.b2 = np.zeros((1, self.gizli_boyutu_2))
        self.W3 = np.random.randn(self.gizli_boyutu_2, self.gizli_boyutu_3) * 0.1
        self.b3 = np.zeros((1, self.gizli_boyutu_3))
        self.W4 = np.random.randn(self.gizli_boyutu_3, self.cikti_boyutu) * 0.1
        self.b4 = np.zeros((1, self.cikti_boyutu))

        # Öğrenme Parametreleri (Hyperparameters)
        self.ogrenme_orani = 0.001  # Ağırlıkların ne kadar hızlı güncelleneceği
        self.gama = 0.95           # Gelecekteki ödüllerin bugünkü değeri (discount factor)
        self.epsilon = 1.0         # Keşif oranı (başlangıçta %100)
        self.epsilon_azalma = 0.995 # Her adımdan sonra keşif oranının azalma miktarı
        self.epsilon_min = 0.01    # Minimum keşif oranı

        # Olası eylemlerin listesi (çıktı nöronlarına karşılık gelir)
        self.eylemler = ['Çalış', 'Yemek Ye', 'Uyu', 'Temizlen', 'Eğitim Al', 'Kitap Oku', 'İş Kur/Yönet']

        # Geri yayılım için ara katmanların çıktılarının saklanması
        self.a1, self.a2, self.a3 = None, None, None


    def _sigmoid(self, x):
        """Sigmoid aktivasyon fonksiyonu."""
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))

    def _sigmoid_turev(self, x):
        """Sigmoid fonksiyonunun türevi."""
        return x * (1 - x)

    def _ileri_yayilim(self, girdiler):
        """
        Sinir ağının ileri yayılım hesaplamasını gerçekleştirir ve ara katman
        sonuçlarını geri yayılım için saklar.
        """
        z1 = np.dot(girdiler, self.W1) + self.b1
        self.a1 = self._sigmoid(z1)
        z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self._sigmoid(z2)
        z3 = np.dot(self.a2, self.W3) + self.b3
        self.a3 = self._sigmoid(z3)
        z4 = np.dot(self.a3, self.W4) + self.b4
        # Çıktı katmanında aktivasyon fonksiyonu kullanmıyoruz (Q-değerleri lineer olabilir)
        return z4

    def _geri_yayilim(self, girdiler, hedef_q_degerleri):
        """
        Hata miktarını hesaplayarak ağın ağırlıklarını geri yayılım ile günceller.
        """
        # Mevcut tahminleri al
        mevcut_q_degerleri = self._ileri_yayilim(girdiler)

        # Hatayı hesapla
        hata = hedef_q_degerleri - mevcut_q_degerleri

        # Geri yayılım
        delta4 = hata
        dW4 = np.dot(self.a3.T, delta4)
        db4 = np.sum(delta4, axis=0, keepdims=True)

        hata3 = np.dot(delta4, self.W4.T)
        delta3 = hata3 * self._sigmoid_turev(self.a3)
        dW3 = np.dot(self.a2.T, delta3)
        db3 = np.sum(delta3, axis=0, keepdims=True)

        hata2 = np.dot(delta3, self.W3.T)
        delta2 = hata2 * self._sigmoid_turev(self.a2)
        dW2 = np.dot(self.a1.T, delta2)
        db2 = np.sum(delta2, axis=0, keepdims=True)

        hata1 = np.dot(delta2, self.W2.T)
        delta1 = hata1 * self._sigmoid_turev(self.a1)
        dW1 = np.dot(girdiler.T, delta1)
        db1 = np.sum(delta1, axis=0, keepdims=True)

        # Ağırlıkları ve sapmaları güncelle
        self.W1 += self.ogrenme_orani * dW1
        self.b1 += self.ogrenme_orani * db1
        self.W2 += self.ogrenme_orani * dW2
        self.b2 += self.ogrenme_orani * db2
        self.W3 += self.ogrenme_orani * dW3
        self.b3 += self.ogrenme_orani * db3
        self.W4 += self.ogrenme_orani * dW4
        self.b4 += self.ogrenme_orani * db4


    def _normalize_state(self, oyuncu, zaman):
        """
        Oyuncu ve zaman durumunu sinir ağı için normalleştirir (0-1 arasına getirir).
        """
        konum_map = {"Ev": 0.0, "Şehir Merkezi": 0.5, "Sanayi Bölgesi": 1.0}
        konum_degeri = konum_map.get(oyuncu.mevcut_konum.ad, 0.0)
        max_para = 10000.0

        state = np.array([
            oyuncu.saglik / 100.0,
            oyuncu.enerji / 100.0,
            oyuncu.aclik / 100.0,
            min(oyuncu.para, max_para) / max_para,
            zaman.saat / 23.0,
            konum_degeri
        ])

        return state.reshape(1, self.girdi_boyutu)

    def karar_ver(self, oyuncu, zaman):
        """
        Epsilon-greedy stratejisi kullanarak bir eylem seçer: Ya en iyi bilinen
        eylemi kullanır ya da yeni bir eylem keşfeder.
        """
        # "Geleceğe yatırım" mantığını burada kaldırdık çünkü AI artık bunu kendi kendine öğrenecek.

        # Keşfet (rastgele eylem) veya kullan (en iyi eylem)
        if np.random.rand() <= self.epsilon:
            secilen_eylem_index = np.random.randint(0, self.cikti_boyutu)
            print(f"--- AI Keşfediyor (Rastgele Eylem) ---")
        else:
            norm_state = self._normalize_state(oyuncu, zaman)
            eylem_guven_skorlari = self._ileri_yayilim(norm_state)
            secilen_eylem_index = np.argmax(eylem_guven_skorlari)

        return secilen_eylem_index, self.eylemler[secilen_eylem_index]

    def ogren(self, durum, eylem_index, odul, sonraki_durum):
        """
        Bir eylemin sonucuna göre (ödül) sinir ağının ağırlıklarını günceller.
        Bu, Q-learning formülünün bir uygulamasıdır.
        """
        # Durumları normalize et
        norm_durum = self._normalize_state(durum['oyuncu'], durum['zaman'])
        norm_sonraki_durum = self._normalize_state(sonraki_durum['oyuncu'], sonraki_durum['zaman'])

        # Mevcut durum için Q-değerlerini tahmin et
        hedef_q = self._ileri_yayilim(norm_durum)

        # Gelecekteki en iyi Q-değerini tahmin et
        gelecek_q = self._ileri_yayilim(norm_sonraki_durum)
        max_gelecek_q = np.max(gelecek_q)

        # Q-learning formülü ile hedef değeri güncelle
        hedef_q[0, eylem_index] = odul + self.gama * max_gelecek_q

        # Ağırlıkları güncellemek için geri yayılımı çalıştır
        self._geri_yayilim(norm_durum, hedef_q)

        # Keşif oranını zamanla azalt
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_azalma
