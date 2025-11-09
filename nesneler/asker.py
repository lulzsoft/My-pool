import pygame

class Asker:
    def __init__(self, x, y, takim_id, renk):
        self.x = x
        self.y = y
        self.hp = 100
        self.saldiri_gucu = 10
        self.takim_id = takim_id
        self.renk = renk
        self.rect = pygame.Rect(self.x, self.y, 20, 20)

    def hareket_et(self, hedef_x, hedef_y):
        # Basit hareket mantığı
        if self.x < hedef_x:
            self.x += 1
        elif self.x > hedef_x:
            self.x -= 1
        if self.y < hedef_y:
            self.y += 1
        elif self.y > hedef_y:
            self.y -= 1
        self.rect.topleft = (self.x, self.y)

    def ciz(self, ekran):
        pygame.draw.rect(ekran, self.renk, self.rect)

class YakinDovuscu(Asker):
    def __init__(self, x, y, takim_id, renk):
        super().__init__(x, y, takim_id, renk)
        self.saldiri_mesafesi = 25

    def saldir(self, hedef):
        mesafe = ((self.x - hedef.x)**2 + (self.y - hedef.y)**2)**0.5
        if mesafe <= self.saldiri_mesafesi:
            hedef.hp -= self.saldiri_gucu
            return True
        return False

class Menzilli(Asker):
    def __init__(self, x, y, takim_id, renk):
        super().__init__(x, y, takim_id, renk)
        self.saldiri_mesafesi = 150

    def saldir(self, hedef, mermiler):
        mesafe = ((self.x - hedef.x)**2 + (self.y - hedef.y)**2)**0.5
        if mesafe <= self.saldiri_mesafesi:
            mermiler.append(Mermi(self.x, self.y, hedef.x, hedef.y, self.saldiri_gucu, self.takim_id))
            return True
        return False

class Mermi:
    def __init__(self, x, y, hedef_x, hedef_y, guc, takim_id):
        self.x = x
        self.y = y
        self.hedef_x = hedef_x
        self.hedef_y = hedef_y
        self.guc = guc
        self.takim_id = takim_id
        self.hiz = 5
        self.rect = pygame.Rect(self.x, self.y, 5, 5)
        self.yon_x = (self.hedef_x - self.x)
        self.yon_y = (self.hedef_y - self.y)
        uzunluk = (self.yon_x**2 + self.yon_y**2)**0.5
        if uzunluk > 0:
            self.yon_x /= uzunluk
            self.yon_y /= uzunluk

    def hareket_et(self):
        self.x += self.yon_x * self.hiz
        self.y += self.yon_y * self.hiz
        self.rect.topleft = (self.x, self.y)

    def ciz(self, ekran):
        pygame.draw.rect(ekran, (255, 255, 0), self.rect)
