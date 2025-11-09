import pygame

class Kaynak:
    """
    Haritada bulunacak ve işçiler tarafından toplanabilecek kaynakları (odun, gıda, maden) temsil eder.
    """
    def __init__(self, x, y, kaynak_tipi, miktar=1000):
        self.x = x
        self.y = y
        self.kaynak_tipi = kaynak_tipi  # "odun", "gıda", "maden"
        self.miktar = miktar
        self.rect = pygame.Rect(x, y, 30, 30)  # Kaynakların haritadaki boyutu

        # Kaynak tipine göre renk belirle
        renkler = {
            "odun": (139, 69, 19),   # Kahverengi
            "gıda": (0, 255, 0),     # Yeşil
            "maden": (128, 128, 128) # Gri
        }
        self.renk = renkler.get(kaynak_tipi, (255, 255, 255))

    def ciz(self, ekran):
        """Kaynağı ekrana çizer."""
        pygame.draw.rect(ekran, self.renk, self.rect)

    def topla(self, toplama_miktari):
        """Kaynaktan belirtilen miktarda eksiltir ve toplanan miktarı döndürür."""
        if self.miktar > 0:
            toplanan = min(self.miktar, toplama_miktari)
            self.miktar -= toplanan
            return toplanan
        return 0
