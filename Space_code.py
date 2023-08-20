'''
Dynamická hra v prostředí PyGame
Kateřina Vejdělková, 1. ročník, MOMP, kruh 54
letní semestr 2023
Programování 2
'''

try:
    # noinspection PyUnresolvedReferences
    import pygame_sdl2

    pygame_sdl2.import_as_pygame()
except ImportError:
    pass
import pygame

#import pygame
from random import randint

# initialize pygame
pygame.init()

# Obrazovka
width = 1200
height = 675
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space game')

# Nastavení maximální hodnoty FPS
fps = 60
clock = pygame.time.Clock()


# Herní classa - převezme: player = skupina objektů classy Player; planets = skupina objektů classy Planet
class Game:
    def __init__(self, player, planets):
        # obecné 'vlastnosti'
        self.score = 0
        self.best = 0                       # proměnná hry, která si zapamatuje výsledek vašeho nejúspěšnějšího kola
        self.speed_acceleration = 0.2       # padající objekty postupně zrychlují o tuto hodnotu
        self.player = player
        self.planets = planets
        self.stimer = 15                    # šablona výchozího nastavení časovače
        self.timer = self.stimer            # proměnná, v níž se odpočítává čas vašeho zrychlení
        self.slow_down_timer = 0            # proměnná pomáhající odpočtu vteřin (více u jějího použití ve funkci fast)
        self.want_escape = False            # tyto tři pomocné proměnné napomáhají ukončení programu nebo odpočtu
        self.start_timer = False
        self.paused = True

        # nastavení fontů písma
        self.pismo_velke = pygame.font.SysFont('Arial', 50)
        self.pismo_male = pygame.font.SysFont('Corbel', 30)

    # kód, který budeme volat stále dokola, pro plynulý chod věcí, které je nutné kontrolovat a provádět nepřetržitě
    def update(self):
        self.check_collisions()

        # jestliže jsme chytily kometu (proměnná True), chceme, abychom byli rychlejší
        if self.start_timer:
            self.fast()

        # ubereme bod, pokud nám planeta proklouzla
        for _ in self.planets:
            if _.type in [0, 1, 2, 3, 4] and _.rect.bottom > height - 100:
                self.score -= 1

    # vykreslíme grafickou stránku hry
    def draw(self):
        white = (255, 255, 255)

        # texty
        score_text = self.pismo_velke.render(f'Score: {self.score}', True, white)
        st_rect = score_text.get_rect()
        st_rect.topright = (width//2 - 10, height - 75)

        lives_text = self.pismo_velke.render(f'Lives: {self.player.lives}', True, white)
        lt_rect = lives_text.get_rect()
        lt_rect.topleft = (width//2 + 10, height - 75)

        best_text = self.pismo_male.render(f'Best: {self.best}', True, white)
        bt_rect = best_text.get_rect()
        bt_rect.topleft = (10, height - 85)

        # vykreslení textu
        screen.blit(score_text, st_rect)
        screen.blit(lives_text, lt_rect)
        screen.blit(best_text, bt_rect)

        # čára oddělující herní pole
        pygame.draw.line(screen, white, (0, height - 100), (width, height - 100), 4)

    # kontrola kolize a příslušné akce z ní vycházející (přičtení bodů, zrychlení planety/hráče, spuštění časovače, ...)
    def check_collisions(self):
        # col_planet = dočasně uložený objekt, se kterým player koliduje
        col_planet = pygame.sprite.spritecollideany(self.player, self.planets)
        # typy planet: 0 = earth, 1, 2, 3, 4, 5 = comet, 6 = meteor
        if col_planet:
            if col_planet.type == 0:
                self.score += 20
                if self.score > self.best:
                    self.best = self.score
                self.player.success_sound.play()
                col_planet.speed[col_planet.type] += self.speed_acceleration   # změna rychlosti ve vlastnostech planety
                col_planet.reset_place()            # planetu vrátíme za okraj, odkud může opět padat
            if col_planet.type in [1, 2, 3, 4]:
                self.score += 10
                if self.score > self.best:
                    self.best = self.score
                self.player.success_sound.play()
                col_planet.speed[col_planet.type] += self.speed_acceleration
                col_planet.reset_place()
            if col_planet.type == 5:
                self.start_timer = True
                self.timer = self.stimer    # tyto dva řádky jsou pro případ, že nám běží odpočet a znovu chytíme kometu
                self.slow_down_timer = 0    # potom totiž chceme odpočítávat od začátku
                self.player.success_sound.play()
                col_planet.speed[col_planet.type] += self.speed_acceleration
                col_planet.reset_place()
            if col_planet.type == 6:
                self.player.lives -= 1
                self.player.wrong_sound.play()
                col_planet.speed[col_planet.type] += self.speed_acceleration
                col_planet.reset_place()
                if self.player.lives == 0:      # jestliže nám dojdou životy, hra končí, obnoví se a čeká, zda chceme pokračovat
                    self.pause_game(f'Your score: {self.score}', 'Want continue? Press enter')
                    self.reset_game()

    # funkce zrychlení po chycení komety
    def fast(self):
        # vykreslíme odpočet času
        timer_text = self.pismo_male.render(f'Timer: {self.timer} s', True, (255, 255, 255))
        tt_rect = timer_text.get_rect()
        tt_rect.bottomleft = (10, height - 15)
        screen.blit(timer_text, tt_rect)
        pygame.display.update()

        # zrychlení hráče
        self.player.speed = 20

        # odpočet času
        self.slow_down_timer += 1       # fps máme 60, tedy za sekundu se zvýší 60x -> ukazuje nám, kdy uplynula vteřina
        if self.slow_down_timer == 60:
            self.slow_down_timer = 0
            self.timer -= 1
            if self.timer == 0:             # vypršel čas -> vše do původního nastavení
                self.timer = self.stimer
                self.player.speed = self.player.sspeed
                self.start_timer = False

    # zastavení hry na začátku a konci, jako parametry zadáme hlavní a menší text, který chceme na obrazovce
    def pause_game(self, main_text, sub_text):
        white = (255, 255, 255)
        space_blue = pygame.Color('#1d1135')

        # zastavení hry a výběr pokračovat/nepokračovat
        self.paused = True
        while self.paused:

            # musíme vykreslovat v cyklu, protože jinak bychom 'nic neviděli' při návratu z cyklu help_screen
            screen.fill(space_blue)
            # text
            self.draw_image(self.pismo_velke.render(main_text, True, white), width//2, height//2 - 20)
            self.draw_image(self.pismo_male.render(sub_text, True, white), width//2, height//2 + 30)
            self.draw_image(self.pismo_male.render('(press H for help)', True, white), width//2, height//2 + 200)

            pygame.display.update()

            for x in pygame.event.get():        # kontrola, co si uživatel přeje za pokračování
                if x.type == pygame.KEYDOWN:
                    if x.key == pygame.K_RETURN:        # pokračovat v místě, odkud byly tato funcke zavolána (hrát hru)
                        self.paused = False
                    elif x.key == pygame.K_ESCAPE:      # úplně ukončit hru
                        self.want_escape = True
                        self.paused = False
                    elif x.key == pygame.K_h:           # dostat se na stránku s nápovědou
                        self.help_screen()
                if x.type == pygame.QUIT:               # úplně ukončit hru
                    self.want_escape = True
                    self.paused = False

    # menší pomocná funkce k vykreslení obrázků/textu
    # parametry funkce jsou: image = vkládaný obrázek/text; x,y = souřadnice středu
    def draw_image(self, image, x, y):  # bohužel nelze použít při umisťování v závislosti na něčem jiném, než je střed
        img = image
        img_rect = img.get_rect()
        img_rect.center = (x, y)
        screen.blit(img, img_rect)

    # obrazovka s nápovědou, která se ukáže po stisknutí písmene h
    def help_screen(self):
        white = (255, 255, 255)
        space_blue = pygame.Color('#1d1135')

        screen.fill(space_blue)

        # obrázky
        self.draw_image(pygame.image.load('images/earth.png'), 284, 127)
        self.draw_image(pygame.image.load('images/planet1.png'), width//2, 127)
        self.draw_image(pygame.image.load('images/planet2.png'), width - 284, 127)
        self.draw_image(pygame.image.load('images/planet3.png'), 284, 327)
        self.draw_image(pygame.image.load('images/planet3.png'), 284, 327)
        self.draw_image(pygame.image.load('images/planet4.png'), width//2, 327)
        self.draw_image(pygame.image.load('images/comet.png'), width - 284, 327)
        self.draw_image(pygame.image.load('images/meteor.png'), 284, 527)

        # texty
        self.draw_image(self.pismo_velke.render('Catch all planets !', True, white), width//2, 38)
        self.draw_image(self.pismo_velke.render('Earth', True, white), 284, 194)
        self.draw_image(self.pismo_velke.render('Greenland', True, white), width//2, 194)
        self.draw_image(self.pismo_velke.render('Orangering', True, white), width - 284, 194)
        self.draw_image(self.pismo_velke.render('Cowplanet', True, white), 284, 394)
        self.draw_image(self.pismo_velke.render('Volcano', True, white), width//2, 394)
        self.draw_image(self.pismo_velke.render('Comet', True, white), width - 284, 394)
        self.draw_image(self.pismo_velke.render('Meteor', True, white), 284, 594)
        self.draw_image(self.pismo_male.render('+20 points', True, white), 284, 244)
        self.draw_image(self.pismo_male.render('+10 points', True, white), width//2, 244)
        self.draw_image(self.pismo_male.render('+10 points', True, white), width - 284, 244)
        self.draw_image(self.pismo_male.render('+10 points', True, white), 284, 444)
        self.draw_image(self.pismo_male.render('+10 points', True, white), width//2, 444)
        self.draw_image(self.pismo_male.render('faster for 15 sc', True, white), width - 284, 444)
        self.draw_image(self.pismo_male.render('-1 live', True, white), 284, 644)
        self.draw_image(self.pismo_male.render('move <, >', True, white), width//2, height - 120)
        self.draw_image(self.pismo_male.render('miss planet = -1 point', True, white), width//2, height - 95)
        self.draw_image(self.pismo_male.render('(press enter to close help page)', True, white), width - 200, height - 30)

        pygame.display.update()

        # cyklus ve který zajišťuje zobrazení nápovědy a pozastavení okolní hry
        help_screen = True
        while help_screen:
            for evt in pygame.event.get():              # identifikace, jak chce uživatel pokračovat
                if evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_RETURN:      # zpět na místo ve hře, odkud se sem dostal
                        help_screen = False
                    elif evt.key == pygame.K_ESCAPE:    # úplně ukončit hru
                        help_screen = False
                        self.paused = False
                        self.want_escape = True
                if evt.type == pygame.QUIT:             # úplně ukončit hru
                    help_screen = False
                    self.paused = False
                    self.want_escape = True

    # tato funkce vrací hru do původního nastavení
    def reset_game(self):
        self.player.reset()
        self.score = 0
        self.start_timer = False
        self.slow_down_timer = 0
        self.timer = self.stimer
        for y in self.planets:
            y.reset_place()
            y.reset_speed()


# classa padajícícho objektu, který se snažíme chytit
# má dědičnost z vestavěné třídy Sprite a jeho parametry jsou: image = obrázek objektu, planet_type = typ objektu
class Planet(pygame.sprite.Sprite):
    def __init__(self, image, planet_type):
        super().__init__()

        # typy planet: 0 = earth, 1, 2, 3, 4, 5 = comet, 6 = meteor
        self.type = planet_type

        # výchozí pozice jednotlivých planet, rychlost - typ určuje index
        self.sspeed = [5, 2, 2, 2, 2, 7, 7]         # šablona pro počáteční rychlosti
        self.speed = self.sspeed                    # seznma aktuálních rychlostí
        self.behind_border = [1000, 200, 150, 100, 250, 5000, 500]

        # nahrání a umístění obrázku v image - libovolně v šířce herního okna (okraj 32, protože umisťujeme střed)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (randint(32, width - 32), 0 - self.behind_border[self.type])

    # kód, který budeme volat stále dokola, pro plynulý chod věcí, které je nutné kontrolovat a provádět nepřetržitě
    def update(self):
        # padání planet
        if self.rect.bottom > height - 100:      # ve výšce 100 nám končí herní pole
            self.reset_place()
        else:
            self.rect.y += self.speed[self.type]

    # vrácení planetky na pozici za okrajem a vrácení původních rychlostí
    def reset_place(self):
        self.rect.center = (randint(32, width - 32), 0 - self.behind_border[self.type])

    def reset_speed(self):
        self.speed = self.sspeed


# classa objektu, kterým pohybuje uživatel, má dědičnost z vestavěné třídy Sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # načtení a umístění do výchozí pozice
        self.image = pygame.image.load('images/cyclops.png')
        self.rect = self.image.get_rect()
        self.rect.center = (width//2, height - 170)     # ve výšce 100 končí herní pole a obrázek je 128x128

        # zvuky
        self.success_sound = pygame.mixer.Sound('sounds/successful_sound.wav')
        self.success_sound.set_volume(0.1)
        self.wrong_sound = pygame.mixer.Sound('sounds/wrong_sound.wav')
        self.wrong_sound.set_volume(0.1)

        # ostatní vlastnosti hráče
        self.slives = 5         # šablona pro výchozí nastavení životů
        self.lives = self.slives
        self.sspeed = 8         # šablona pro výchozí nastavení rychlosti
        self.speed = self.sspeed

    # kód, který budeme volat stále dokola, pro plynulý chod věcí, které je nutné kontrolovat a provádět nepřetržitě
    def update(self):
        # pohyb klávesami šipek
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += self.speed

    # návrat hráče do výchozí pozice
    def reset(self):
        self.rect.center = (width//2, height - 170)
        self.speed = self.sspeed
        self.lives = self.slives


# skupina hráčů - je sice jeden, ale vlastnosti třídy Group se nám ve hře budou hodit
player_group = pygame.sprite.Group()
one_player = Player()
player_group.add(one_player)

# skupina planet
planet_group = pygame.sprite.Group()
# typy planet: 0 = earth, 1, 2, 3, 4, 5 = comet, 6 = meteor
pl = Planet(pygame.image.load('images/earth.png'), 0)
planet_group.add(pl)
pl = Planet(pygame.image.load('images/planet1.png'), 1)
planet_group.add(pl)
pl = Planet(pygame.image.load('images/planet2.png'), 2)
planet_group.add(pl)
pl = Planet(pygame.image.load('images/planet3.png'), 3)
planet_group.add(pl)
pl = Planet(pygame.image.load('images/planet4.png'), 4)
planet_group.add(pl)
pl = Planet(pygame.image.load('images/comet.png'), 5)
planet_group.add(pl)
pl = Planet(pygame.image.load('images/meteor.png'), 6)
planet_group.add(pl)

# objekt Game
my_game = Game(one_player, planet_group)
my_game.pause_game('Space game', 'Press enter to start game')

# hlavní herní cyklus
lets_continue = True
while lets_continue:
    if my_game.want_escape:     # tato promměnná kontroluje, zda nechceme opustit hru ve fázi paused
        break
    for event in pygame.event.get():    # kontrola, zda chce hráč opustit hru nebo otevřít nápovědu
        if event.type == pygame.QUIT:
            lets_continue = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            lets_continue = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            my_game.help_screen()

    screen.fill(pygame.Color('#1d1135'))
    # Updatování skupiny hráče
    player_group.draw(screen)
    player_group.update()
    # Updatování skupiny planet
    planet_group.draw(screen)
    planet_group.update()
    # Updatování objekt Game
    my_game.draw()
    my_game.update()

    # Update obrazovky
    pygame.display.update()

    # zpomalení cyklu
    clock.tick(fps)

# close pygame
pygame.quit()
