import pygame
import math
import random

class Asker:
    """Tüm birimler için temel sınıf (Askerler, İşçiler vb.)."""
    def __init__(self, x, y, takim_id, renk, hp=100, guc=10, hiz=2):
        self.x = x
        self.y = y
        self.takim_id = takim_id
        self.renk = renk
        self.hp = hp
        self.max_hp = hp
        self.guc = guc
        self.hiz = hiz
        self.rect = pygame.Rect(x, y, 15, 15)
        self.hedef = None
        self.gorev = None # "topla", "insa_et", "saldir", "bos"
        self.gorev_hedefi = None

    def ciz(self, ekran):
        """Birimi ve can barını ekrana çizer."""
        pygame.draw.circle(ekran, self.renk, (self.x, self.y), 8)
        # Can barı
        if self.hp < self.max_hp:
            can_bari_uzunluk = 20
            can_bari_kalan = (self.hp / self.max_hp) * can_bari_uzunluk
            can_bari_rect = pygame.Rect(self.x - 10, self.y - 15, can_bari_uzunluk, 3)
            kalan_can_rect = pygame.Rect(self.x - 10, self.y - 15, can_bari_kalan, 3)
            pygame.draw.rect(ekran, (255, 0, 0), can_bari_rect)
            pygame.draw.rect(ekran, (0, 255, 0), kalan_can_rect)

    def hareket_et(self, hedef_x, hedef_y):
        """Birim, hedefe doğru hareket eder."""
        dx = hedef_x - self.x
        dy = hedef_y - self.y
        mesafe = math.sqrt(dx**2 + dy**2)
        if mesafe > 1:
            self.x += (dx / mesafe) * self.hiz
            self.y += (dy / mesafe) * self.hiz
            self.rect.center = (int(self.x), int(self.y))

    def mesafe_hesapla(self, hedef):
        return math.sqrt((self.x - hedef.x)**2 + (self.y - hedef.y)**2)

class Isci(Asker):
    """Kaynak toplayan ve bina inşa eden birim."""
    def __init__(self, x, y, takim_id, renk):
        super().__init__(x, y, takim_id, renk, hp=50, guc=0, hiz=2.5)
        self.tasiyor = None # "odun", "gıda", "maden" veya None
        self.tasiyor_miktar = 0
        self.toplama_suresi = 0
        self.insa_suresi = 0

    def gorev_ata(self, gorev, hedef):
        self.gorev = gorev
        self.gorev_hedefi = hedef
        self.hedef = hedef

    def guncelle(self, ana_bina):
        """İşçinin görev mantığını günceller."""
        if self.gorev == "topla":
            if self.tasiyor and self.tasiyor_miktar > 0:
                # Ana üsse geri dön ve kaynağı bırak
                self.hedef = ana_bina
                if self.mesafe_hesapla(ana_bina) < 20:
                    # Kaynağı bırakma mantığı burada eklenecek
                    kaynak_tipi = self.tasiyor
                    miktar = self.tasiyor_miktar
                    self.tasiyor = None
                    self.tasiyor_miktar = 0
                    self.gorev = "bos"
                    self.hedef = None
                    return ("kaynak_birak", kaynak_tipi, miktar)
            else:
                # Kaynak noktasına git ve topla
                self.hedef = self.gorev_hedefi
                if self.mesafe_hesapla(self.gorev_hedefi) < 10:
                    self.toplama_suresi += 1
                    if self.toplama_suresi >= 60: # 1 saniye bekle
                        self.tasiyor = self.gorev_hedefi.kaynak_tipi
                        self.tasiyor_miktar = self.gorev_hedefi.topla(10)
                        self.toplama_suresi = 0

        elif self.gorev == "insa_et":
            # İnşaat alanına git
            if self.mesafe_hesapla(self.gorev_hedefi) < 20:
                self.insa_suresi += 1
                if self.insa_suresi >= 300: # 5 saniye
                    self.gorev = "bos"
                    self.hedef = None
                    return ("insa_et_tamamla", self.gorev_hedefi)

        # Görev varsa ve hedef belliyse hareket et
        if self.hedef:
            self.hareket_et(self.hedef.x, self.hedef.y)

        return None

class YakinDovuscu(Asker):
    def __init__(self, x, y, takim_id, renk):
        super().__init__(x, y, takim_id, renk, hp=120, guc=15, hiz=2.2)
        self.saldiri_menzili = 20
        self.saldiri_hizi = 60 # Saniyede 1 vuruş

    def saldir(self, hedef):
        if self.mesafe_hesapla(hedef) <= self.saldiri_menzili:
            hedef.hp -= self.guc
            return True
        return False

class Menzilli(Asker):
    def __init__(self, x, y, takim_id, renk):
        super().__init__(x, y, takim_id, renk, hp=80, guc=10, hiz=1.8)
        self.saldiri_menzili = 150
        self.saldiri_hizi = 90 # 1.5 saniyede 1 atış
        self.saldiri_suresi = 0

    def saldir(self, hedef, mermiler):
        self.saldiri_suresi += 1
        if self.mesafe_hesapla(hedef) <= self.saldiri_menzili and self.saldiri_suresi >= self.saldiri_hizi:
            self.saldiri_suresi = 0
            mermiler.append(Mermi(self.x, self.y, hedef, self.takim_id, self.guc))
            return True
        return False

class Mermi:
    def __init__(self, x, y, hedef, takim_id, guc):
        self.x = x
        self.y = y
        self.hedef = hedef
        self.takim_id = takim_id
        self.guc = guc
        self.hiz = 10
        self.rect = pygame.Rect(x, y, 5, 5)

    def hareket_et(self):
        if not self.hedef: return
        dx = self.hedef.x - self.x
        dy = self.hedef.y - self.y
        mesafe = math.sqrt(dx**2 + dy**2)
        if mesafe > 1:
            self.x += (dx / mesafe) * self.hiz
            self.y += (dy / mesafe) * self.hiz
            self.rect.center = (int(self.x), int(self.y))

    def ciz(self, ekran):
        pygame.draw.circle(ekran, (255, 255, 0), (int(self.x), int(self.y)), 3)
