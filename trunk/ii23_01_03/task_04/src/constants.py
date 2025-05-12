import pygame as pg

res = screen_width, screen_height = 1000, 600
fps = 60
score = 0
screen = pg.display.set_mode(res)

pg.font.init()
textfont = pg.font.Font('font.TTF', 80)
textfont_small = pg.font.Font('font.TTF', 40)
text_gameover = textfont.render('GAME   OVER', True, pg.Color('red'))
text_youwin = textfont.render('YOU   WIN!', True, pg.Color('green'))
text_reload = textfont_small.render('Press   R   to  restart', True, pg.Color('white'))

colors = ['magenta', 'yellow', 'cyan', 'blue2', 'green', 'deeppink', 'red']
bonuses = ['platform.resize(1.25)', 'platform.resize(0.8)',
           'for b in balls: ball.speed = int(0.8 * ball.speed)', 'for b in balls: ball.speed = int(1.25 * ball.speed)',
           'balls.append(Ball(platform.body.center[0], platform.body.top - 12))']
bonus_balls = []
balls = []
bonus_colors = {bonuses[0]: pg.Color('green'),
                bonuses[1]: pg.Color('red'),
                bonuses[2]: pg.Color('forestgreen'),
                bonuses[3]: pg.Color('orange'),
                bonuses[4]: pg.Color('white')}