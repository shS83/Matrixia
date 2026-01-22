import pygame
from pygame.locals import *
import random
from enum import Enum

class State(Enum):
    """ The name of the game """
    NONE = 0
    PARTYMODE = 1
    GRAYSCALE = 2
    CYCLIST = 3
    RANDO = 4
    DOUBLETROUBLE = 5
    FULLSCREEN = 6
    REVERSE = 7


pygame.init()
timer = pygame.time.Clock()
info_object = pygame.display.Info()
xRES, yRES = info_object.current_w, info_object.current_h
screen = pygame.display.set_mode([xRES, yRES], RESIZABLE)
startTime = pygame.time.get_ticks()
font_size = 21
font = pygame.font.Font('VL-Gothic-Regular.ttf', font_size)
pygame.display.set_icon(font.render("シ", True, (0, 255, 0)))
running = True

MIDNIGHT_BLUE = (20, 20, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 115, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ALL_COLORS = [WHITE, BLUE, BLACK, GREEN, ORANGE, YELLOW, RED, MIDNIGHT_BLUE, MAGENTA, PURPLE, CYAN]

current_cycle = None
color = None
STATUS = State.NONE
letters: int = 100000
katakana: str = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヰヱヲン"
all_letters: list = []
fs: tuple = font.size('gZ')

class Fadeout:
    """ Fadeout unto darkness """
    global STATUS

    def __init__(self, obj: pygame.Surface, delay: float):
        self.object = obj
        self.delay = delay
        self.alpha = 255

    def fade_out(self) -> pygame.Surface:
        if (self.delay <= 0) and (self.alpha > 0):
            self.alpha -= 1
            self.object.set_alpha(self.alpha)
        self.delay -= 1
        return self.object.copy()

class Descender:
    """ Descent unto madness """
    global WHITE, BLACK, GREEN, ORANGE, YELLOW, RED, BLUE, MAGENTA, PURPLE, CYAN, MIDNIGHT_BLUE, ALL_COLORS, current_cycle, xRES, yRES, screen
    def __init__(self, x):
        self.y = -20
        self.x = x
        self.color = WHITE
        self.trail = 35
        self.olds = []
        self.currframe = 1
        self.y_space = self.trail + 80

    def descend(self, char: str) -> bool | None:
        global color, xRES, fs, all_letters
        fontsize = font.size("gZ")
        counter = 1

        if self.y < yRES + self.y_space:
            text = font.render(char, True, GREEN)
            match STATUS:
                case State.PARTYMODE:
                    # Partymode
                    text = font.render(char, True, random.choice(ALL_COLORS))
                case State.GRAYSCALE:
                    # Grayscale
                    text = font.render(char, True, WHITE)
                case State.CYCLIST:
                    # Cycled color
                    text = font.render(char, True, color)
                case State.RANDO:
                    # Random color
                    text = font.render(char, True, random_color)
                case State.DOUBLETROUBLE:
                    # Double random colors
                    text = font.render(char, True, rando(), rando())
                case State.NONE:
                    # Default green color
                    text = font.render(char, True, GREEN)
                case _:
                    # Obsolete
                    ...
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

        self.y += fontsize[1]

        if self.y > yRES:
            if len(self.olds) > 0:
                self.olds.pop(0)
                return True
            else:
                return False
        
        return True


a: object = Descender(fs[0])
all_letters.append(a)
toast: pygame.Surface = pygame.Surface((500, 300))
pygame.draw.rect(toast, WHITE, ((0, 0), (500, 300)))
pygame.draw.rect(toast, MIDNIGHT_BLUE, ((5, 5), (490, 290)))
smaller_font = pygame.font.Font('VL-Gothic-Regular.ttf', 16)
toast.blit(font.render("Instructions:", True, ORANGE), (15, 15))
toast.blit(smaller_font.render("+ = increase font size", True, YELLOW), (15, 60))
toast.blit(smaller_font.render("- = decrease font size", True, YELLOW), (15, 80))
toast.blit(smaller_font.render("r = Random color", True, CYAN), (15, 100))
toast.blit(smaller_font.render("p = Party mode", True, GREEN), (15, 120))
toast.blit(smaller_font.render("g = Grayscale", True, WHITE), (15, 140))
toast.blit(smaller_font.render("c = Cycle through colors", True, PURPLE), (15, 160))
toast.blit(smaller_font.render("d = Double random colors", True, ORANGE), (15, 180))
toast.blit(smaller_font.render("f = fullscreen", True, MAGENTA), (15, 200))
toast.blit(smaller_font.render("i = this info toastie", True, WHITE), (15, 220))
toast.blit(smaller_font.render("ESCAPE = Quit", True, RED), (15, 250))
fader = Fadeout(toast, 50)
temp_color = ALL_COLORS.copy()
random_color = None


def cyclist():
    global current_cycle, ALL_COLORS, temp_color
    try:
        colour = temp_color.pop(0)
    except IndexError:
        temp_color = ALL_COLORS.copy()
        colour = temp_color.pop(0)
    return colour

def rando():
    global random_color
    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return random_color

while running:

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_KP_PLUS or event.key == K_PLUS:
                font_size += 1
                font = font.Font('VL-Gothic-Regular.ttf', font_size)
            elif event.key == K_KP_MINUS or event.key == K_MINUS and font_size > 0:
                font_size -= 1
                font = font.Font('VL-Gothic-Regular.ttf', font_size)
            elif event.key == K_p:
                if not STATUS.NONE:
                    STATUS = State.NONE
                else:
                    STATUS = State.PARTYMODE
            elif event.key == K_g:
                if not STATUS.NONE:
                    STATUS = State.NONE
                else:
                    STATUS = State.GRAYSCALE
            elif event.key == K_c:
                STATUS = State.CYCLIST
                color = cyclist()
            elif event.key == K_r:
                STATUS = State.RANDO
                random_color = rando()
            elif event.key == K_d:
                STATUS = State.DOUBLETROUBLE
                random_color = rando()
            elif event.key == K_f:
                if STATUS == State.FULLSCREEN:
                    STATUS = State.NONE
                    pygame.display.set_mode((1024, 768), RESIZABLE, 32)
                else:
                    STATUS = State.FULLSCREEN
                    pygame.display.set_mode(pygame.display.get_surface().get_size(), FULLSCREEN, 32)
            elif event.key == K_i:
                toast.set_alpha(255)
                fader = Fadeout(toast, 100)
            elif event.key == K_BACKSPACE:
                if STATUS == State.REVERSE:
                    STATUS = State.NONE
                else:
                    STATUS = State.REVERSE
        if event.type == QUIT:
            running = False

    screen.fill((0, 0, 0))
    pygame.display.set_caption(f"{str(len(all_letters))}x of something is still nonething")

    if len(all_letters) < letters:
        xRES, yRES = screen.get_size()
        fs = font.size("gZ")
        if STATUS == State.DOUBLETROUBLE:
            for _ in range(2):
                blocks = int(xRES / fs[0])
                rand_x = fs[0] * random.randint(0, blocks)
                b = Descender(rand_x)
                all_letters.append(b)
        else:
            blocks = int(xRES / fs[0])
            rand_x = fs[0] * random.randint(0, blocks)
            b = Descender(rand_x)
            all_letters.append(b)

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

pygame.quit()