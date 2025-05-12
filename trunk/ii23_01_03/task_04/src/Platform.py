from constants import screen, screen_height, screen_width, pg


class Platform:
    def __init__(self):
        self.width = 150
        self.height = 10
        self.speed = 10
        self.body = pg.Rect(screen_width // 2 - self.width // 2, screen_height - self.height - 5,
                            self.width, self.height)
        self.color = pg.Color('magenta')

    def resize(self, k):
        pg.draw.rect(screen, pg.Color('white'), self.body)
        self.body = self.body.inflate((k-1) * self.width, 0)

    def draw(self, col=None):
        color = col if col else self.color
        pg.draw.rect(screen, color, self.body, border_radius=3)