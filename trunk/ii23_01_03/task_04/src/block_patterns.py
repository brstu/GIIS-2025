from Block import Block
from random import choice
from constants import colors, screen_width


blocks1 = [Block(10+120*i, 10+70*j, 100, 30, choice(colors))
           for i in range(screen_width // 120) for j in range(4)]
blocks2 = [Block(10+120*i, 10+50*j, 100, 30, choice(colors))
           for j in range(5) for i in range(j, screen_width // 120 - j)]
blocks3 = [Block(10+120*i, 10+50*(4-j), 100, 30, choice(colors))
           for j in range(5) for i in range(j, screen_width // 120 - j)]
blocks_test = [Block(1100, 120, 100, 30, choice(colors)),
               Block(500, 120, 100, 30, choice(colors))]
patterns = [blocks1, blocks2, blocks3]