import numpy as np

class OgrenenYapayZeka:
    def __init__(self, durum_boyutu, eylem_sayisi, ogrenme_orani=0.001, indirim_faktoru=0.95):
        self.durum_boyutu = durum_boyutu
        self.eylem_sayisi = eylem_sayisi
        self.ogrenme_orani = ogrenme_orani
        self.indirim_faktoru = indirim_faktoru
        self.epsilon = 1.0  # Keşif oranı
        self.epsilon_azalma = 0.995
        self.epsilon_min = 0.01

        self.model = self._model_olustur()

    def _model_olustur(self):
        model = {
            'w1': np.random.randn(self.durum_boyutu, 32) * 0.1,
            'b1': np.zeros((1, 32)),
            'w2': np.random.randn(32, 32) * 0.1,
            'b2': np.zeros((1, 32)),
            'w3': np.random.randn(32, self.eylem_sayisi) * 0.1,
            'b3': np.zeros((1, self.eylem_sayisi))
        }
        return model

    def _ileri_yayilim(self, durum):
        # Durumu modele uygun hale getir
        if durum.ndim == 1:
            durum = durum.reshape(1, -1)

        self.z1 = np.dot(durum, self.model['w1']) + self.model['b1']
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.model['w2']) + self.model['b2']
        self.a2 = np.tanh(self.z2)
        q_degerleri = np.dot(self.a2, self.model['w3']) + self.model['b3']
        return q_degerleri

    def eylem_sec(self, durum):
        if np.random.rand() <= self.epsilon:
            return np.random.randint(self.eylem_sayisi)
        q_degerleri = self._ileri_yayilim(durum)
        return np.argmax(q_degerleri)

    def ogren(self, durum, eylem, odul, yeni_durum, bitti):
        durum = durum.reshape(1, -1)
        yeni_durum = yeni_durum.reshape(1, -1)

        # Hedef Q-değerini hesapla
        hedef_q = self._ileri_yayilim(durum).copy()
        gelecek_q = self._ileri_yayilim(yeni_durum)

        if bitti:
            hedef_q[0, eylem] = odul
        else:
            hedef_q[0, eylem] = odul + self.indirim_faktoru * np.max(gelecek_q)

        # Geriye yayılım (Backpropagation) ile ağırlıkları güncelle
        # Çıktı katmanı hatası
        hata_3 = hedef_q - self._ileri_yayilim(durum)
        dw3 = np.dot(self.a2.T, hata_3)

        # Gizli katman 2 hatası
        hata_2 = np.dot(hata_3, self.model['w3'].T) * (1 - np.power(self.a2, 2))
        dw2 = np.dot(self.a1.T, hata_2)

        # Gizli katman 1 hatası
        hata_1 = np.dot(hata_2, self.model['w2'].T) * (1 - np.power(self.a1, 2))
        dw1 = np.dot(durum.T, hata_1)

        # Ağırlıkları güncelle
        self.model['w1'] += self.ogrenme_orani * dw1
        self.model['b1'] += self.ogrenme_orani * np.sum(hata_1, axis=0, keepdims=True)
        self.model['w2'] += self.ogrenme_orani * dw2
        self.model['b2'] += self.ogrenme_orani * np.sum(hata_2, axis=0, keepdims=True)
        self.model['w3'] += self.ogrenme_orani * dw3
        self.model['b3'] += self.ogrenme_orani * np.sum(hata_3, axis=0, keepdims=True)

        # Epsilon'u azaltarak keşfi zamanla düşür
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_azalma
