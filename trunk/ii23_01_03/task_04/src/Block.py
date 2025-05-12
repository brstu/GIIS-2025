from constants import screen, pg


class Block:
    def __init__(self, x, y, w, h, color):
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.body = pg.Rect(self.x, self.y, self.width, self.height)
        self.color = color
        self.bonus = None
        self.bonus_effect = None  # Добавим переменную для хранения эффекта бонуса

    def draw(self, col=None):
        color = col if col else self.color
        pg.draw.rect(screen, color, self.body, border_radius=3)

