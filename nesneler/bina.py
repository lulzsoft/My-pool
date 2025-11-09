import pygame

class Bina:
    """
    Oyundaki tüm binalar için temel sınıf.
    """
    def __init__(self, x, y, takim_id, renk, can=500):
        self.x = x
        self.y = y
        self.takim_id = takim_id
        self.renk = renk
        self.hp = can
        self.max_hp = can
        self.rect = pygame.Rect(x, y, 60, 60) # Binaların boyutu

    def ciz(self, ekran):
        """Binayı ve can barını ekrana çizer."""
        # Ana bina karesi
        pygame.draw.rect(ekran, self.renk, self.rect)
        # Sınır çizgisi
        pygame.draw.rect(ekran, (255, 255, 255), self.rect, 2)

        # Can barı
        can_bari_uzunluk = self.rect.width
        can_bari_kalan = (self.hp / self.max_hp) * can_bari_uzunluk
        can_bari_rect = pygame.Rect(self.x, self.y - 10, can_bari_uzunluk, 5)
        kalan_can_rect = pygame.Rect(self.x, self.y - 10, can_bari_kalan, 5)

        pygame.draw.rect(ekran, (255, 0, 0), can_bari_rect)
        pygame.draw.rect(ekran, (0, 255, 0), kalan_can_rect)


class Kisla(Bina):
    """
    Asker üretmek için kullanılan bina.
    """
    def __init__(self, x, y, takim_id, renk):
        super().__init__(x, y, takim_id, renk, can=1000)
        self.uretim_kuyrugu = []
        self.uretim_suresi = 0
        self.uretim_noktasi = (self.x + self.rect.width + 10, self.y + self.rect.height // 2)

    def birim_uret(self, birim_tipi):
        """Üretim kuyruğuna yeni bir birim ekler."""
        self.uretim_kuyrugu.append(birim_tipi)
        # Basit bir üretim süresi mekanizması
        if not self.uretim_suresi and self.uretim_kuyrugu:
            self.uretim_suresi = 180 # 3 saniye (60 FPS'de)

    def guncelle(self):
        """Üretim sürecini günceller ve tamamlanan birimleri döndürür."""
        if self.uretim_suresi > 0:
            self.uretim_suresi -= 1
            if self.uretim_suresi == 0 and self.uretim_kuyrugu:
                uretilen_birim = self.uretim_kuyrugu.pop(0)
                # Bir sonraki birim için süreyi tekrar başlat
                if self.uretim_kuyrugu:
                    self.uretim_suresi = 180
                return uretilen_birim
        return None
