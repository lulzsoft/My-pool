import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os

class NoralAg(nn.Module):
    """AI için karar mekanizması olarak hizmet edecek olan ileri beslemeli nöral ağ."""
    def __init__(self, girdi_boyutu, cikti_boyutu):
        super(NoralAg, self).__init__()
        self.katman1 = nn.Linear(girdi_boyutu, 128)
        self.katman2 = nn.Linear(128, 128)
        self.katman3 = nn.Linear(128, cikti_boyutu)

    def forward(self, durum):
        x = F.relu(self.katman1(durum))
        x = F.relu(self.katman2(x))
        return self.katman3(x)

class AIAjan:
    def __init__(self, takim_id, girdi_boyutu, eylem_sayisi, model_kayit_yolu=None):
        self.takim_id = takim_id
        self.eylem_sayisi = eylem_sayisi
        self.model = NoralAg(girdi_boyutu, eylem_sayisi)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.hafiza = [] # (durum, eylem, ödül, sonraki_durum, bitti)
        self.hafiza_kapasitesi = 10000

        self.model_kayit_yolu = model_kayit_yolu
        if self.model_kayit_yolu:
            self.modeli_yukle()

    def eylem_sec(self, durum, kesif_orani=0.1):
        """Verilen duruma göre, keşif (rastgele) veya sömürü (model) yaparak bir eylem seçer."""
        if np.random.rand() < kesif_orani:
            return np.random.randint(self.eylem_sayisi)
        else:
            with torch.no_grad():
                durum_tensor = torch.FloatTensor(np.array(durum)).unsqueeze(0)
                eylem_degerleri = self.model(durum_tensor)
                return torch.argmax(eylem_degerleri).item()

    def hatirla(self, durum, eylem, odul, sonraki_durum, bitti):
        """Deneyimleri hafızaya kaydeder."""
        if len(self.hafiza) >= self.hafiza_kapasitesi:
            self.hafiza.pop(0)
        self.hafiza.append((durum, eylem, odul, sonraki_durum, bitti))

    def ogren(self, batch_boyutu=64, gamma=0.99):
        """Hafızadan rastgele bir 'batch' alarak modeli eğitir."""
        if len(self.hafiza) < batch_boyutu:
            return

        batch = np.random.choice(len(self.hafiza), batch_boyutu, replace=False)

        durumlar, eylemler, oduller, sonraki_durumlar, bittiler = [], [], [], [], []
        for i in batch:
            d, e, o, sd, b = self.hafiza[i]
            durumlar.append(d)
            eylemler.append(e)
            oduller.append(o)
            sonraki_durumlar.append(sd)
            bittiler.append(b)

        durumlar = torch.FloatTensor(np.array(durumlar))
        eylemler = torch.LongTensor(eylemler)
        oduller = torch.FloatTensor(oduller)
        sonraki_durumlar = torch.FloatTensor(np.array(sonraki_durumlar))
        bittiler = torch.BoolTensor(bittiler)

        # Mevcut durumlar için Q değerlerini al
        mevcut_q_degerleri = self.model(durumlar).gather(1, eylemler.unsqueeze(1))

        # Sonraki durumlar için maksimum Q değerlerini hesapla
        sonraki_q_degerleri = self.model(sonraki_durumlar).max(1)[0].detach()
        sonraki_q_degerleri[bittiler] = 0.0

        # Hedef Q değerlerini hesapla
        hedef_q_degerleri = oduller + (gamma * sonraki_q_degerleri)

        # Kayıp (loss) fonksiyonunu hesapla
        kayip = F.mse_loss(mevcut_q_degerleri.squeeze(), hedef_q_degerleri)

        # Geri yayılım (backpropagation)
        self.optimizer.zero_grad()
        kayip.backward()
        self.optimizer.step()

    def modeli_kaydet(self):
        """Eğitilmiş modeli dosyaya kaydeder."""
        if self.model_kayit_yolu:
            print(f"Takım {self.takim_id} modeli kaydediliyor: {self.model_kayit_yolu}")
            torch.save(self.model.state_dict(), self.model_kayit_yolu)

    def modeli_yukle(self):
        """Daha önce kaydedilmiş modeli dosyadan yükler."""
        if self.model_kayit_yolu and os.path.exists(self.model_kayit_yolu):
            print(f"Takım {self.takim_id} modeli yükleniyor: {self.model_kayit_yolu}")
            self.model.load_state_dict(torch.load(self.model_kayit_yolu))
            self.model.eval() # Modeli değerlendirme moduna al
        else:
            print(f"Takım {self.takim_id} için kayıtlı model bulunamadı, yeni model oluşturuluyor.")
