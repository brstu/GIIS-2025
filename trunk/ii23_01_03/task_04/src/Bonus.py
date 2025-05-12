from constants import bonus_colors, pg, screen, screen_height
from Block import Block


class Bonus:
    def __init__(self, block: Block):
        self.center = block.body.center  # centers of block and its bonus ball are the same
        self.r = 7
        self.x = self.center[0] - self.r
        self.y = self.center[1] + self.r
        self.R = int(self.r * (2 ** 0.5))
        self.speed = 3
        self.body = pg.Rect(self.x, self.y, 2 * self.r, 2 * self.r)
        self.bonus = block.bonus  # block parameter bonus (effect of a bonus) is transfered to a ball bonus
        self.dy = 1
        self.dx = 0
        self.color = bonus_colors[block.bonus]
        self.image = pg.Surface((self.r, self.r))

    def draw(self):
        pg.draw.circle(screen, self.color, self.center, self.R)

    def drop(self):
        self.body.y += self.dy * self.speed
        self.center = self.body.x + self.r, self.body.y + self.r

    def IsOut(self):
        return self.center[1] - self.R > screen_height