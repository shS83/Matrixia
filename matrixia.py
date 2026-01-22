import pygame
import pygame.gfxdraw
import random
import math
import string

NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
info_object = pygame.display.Info()
xRES, yRES = info_object.current_w, info_object.current_h
screen = pygame.display.set_mode([xRES, yRES], pygame.RESIZABLE)
startTime = pygame.time.get_ticks()
FONT_SIZE = 21
font = pygame.font.SysFont('vl gothic', FONT_SIZE)
running = True
MIDNIGHT_BLUE = (20, 20, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 115, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ALL_COLORS = [WHITE, BLACK, GREEN, ORANGE, YELLOW, RED, MIDNIGHT_BLUE]
RANDOMEVENT = pygame.USEREVENT + 5

class Fadeout:
    def __init__(self, obj: pygame.Surface, delay: float):
        # self.display = display
        self.object = obj
        self.delay = delay
        # self.position = position
        self.alpha = 255

    def fade_out(self) -> pygame.Surface:
        if (self.delay <= 0) and (self.alpha > 0):
            self.alpha -= 1
            self.object.set_alpha(self.alpha)
        self.delay -= 1
        return self.object.copy()

    # def update(self):
    #    self.display.blit(self.object, self.position)

class Descender:

    def __init__(self, x):
        self.y = -20
        self.x = x
        self.color = WHITE
        self.trail = 35
        self.olds = []
        self.currframe = 1
        self.y_space = 80

    def descend(self, char):
        font_size = font.size("gZ")
        counter = 1

        if self.y < yRES:
            text = font.render(char, True, (0, 255, 0))
            pos = (self.x, self.y)
            text.set_alpha(255)
            screen.blit(text, pos)

            if len(self.olds) <= self.trail:
                self.currframe += 1
                self.olds.append((text, pos))
            else:
                self.currframe = 1
                self.olds.pop(0)
                self.olds.append((text, pos))
    
        for i in range(len(self.olds)-1, 0, -1):
            t, p = self.olds[i]
            t.set_alpha(255-(255/self.trail*counter))
            if i == len(self.olds)-1:
                t = font.render(char, True, WHITE)
            screen.blit(t, p)
            counter += 1

        self.y += font_size[1]

        if self.y > yRES:
            if len(self.olds) > 0:
                self.olds.pop(0)
                return True
            else:
                return False
        
        return True


LETTERS: int = 100000
katakana: str = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヰヱヲン"
all_letters: list = []
fs: tuple = font.size('gZ')

def scaler(size):
    font_scaled: list = []
    factor: float = (screen.get_size()[0] / fs[0]) + (screen.get_size()[1] / fs[1]) // 2 * 0.01
    print(f"font-size: {fs}")
    print(f"factor: {factor}")
    font_scaled.append([fs[0], fs[1]])
    font_scaled[0][0] %= int(round(factor))
    font_scaled[0][1] %= int(round(factor))
    size = tuple(font_scaled[0])
    return size

fs = scaler(fs)
print(f"font-size: {fs}")
a: object = Descender(fs[0])
all_letters.append(a)
toast: pygame.Surface = pygame.Surface((300, 150))
pygame.draw.rect(toast, WHITE, ((0, 0), (300, 150)))
pygame.draw.rect(toast, MIDNIGHT_BLUE, ((5, 5), (290, 140)))
smaller_font = pygame.font.SysFont('vl gothic', 16)
toast.blit(font.render("Instructions:", True, ORANGE), (15, 15))
toast.blit(smaller_font.render("KEYPAD + = increase font size", True, YELLOW), (15, 60))
toast.blit(smaller_font.render("KEYPAD - = decrease font size", True, YELLOW), (15, 80))
toast.blit(smaller_font.render("ESCAPE = Quit", True, YELLOW), (15, 100))
toast.blit(smaller_font.render("P = Party mode", True, WHITE), (15, 120))
fader = Fadeout(toast, 50)

while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_KP_PLUS:
                FONT_SIZE += 1
                font = pygame.font.SysFont('vl gothic', FONT_SIZE)
            if event.key == pygame.K_KP_MINUS and FONT_SIZE > 0:
                FONT_SIZE -= 1
                font = pygame.font.SysFont('vl gothic', FONT_SIZE)
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    
    if len(all_letters) < LETTERS:
        xRES, yRES = screen.get_size()
        fs = scaler(fs)
        blocks = int(xRES / fs[0])
        rand_x = fs[0] * random.randint(0, blocks)
        b = Descender(rand_x)
        all_letters.append(b)

        # Let's do two at the time
        # rand_x = fs[0] * random.randint(0, blocks)
        # b = Descender(rand_x)
        # all_letters.append(b)

    for letter in all_letters:
        a = chr(random.randrange(60, 97 + 26))
        c = katakana[random.randint(0,len(katakana)-1)]
        chance = random.choice([a, c])
        a = chance
        if not letter.descend(a):
            all_letters.remove(letter)

    toast = fader.fade_out()
    screen.blit(toast, (10, 10))


    pygame.time.wait(25)

    pygame.display.flip()
    timer.tick(159)