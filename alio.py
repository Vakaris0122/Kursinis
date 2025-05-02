from __future__ import annotations
import pygame
import random
import time
import os
import sys

# ----------------- Singleton HighScore Manager ----------------------
class SingletonMeta(type):
    """Vieno objekto tikslumas: užtikrina, kad bus sukurtas tik vienas HighScoreManager objektas."""
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        """Jei objektas dar nėra sukurtas, sukuria jį, priešingu atveju grąžina jau sukurtą objektą."""
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

class HighScoreManager(metaclass=SingletonMeta):
    """Tvarko aukščiausio įvertinimo įkėlimą ir išsaugojimą į diską."""
    def __init__(self, filename: str):
        """Inicializuoja HighScoreManager ir įkelia aukščiausią rezultatą iš failo."""
        self.filename = filename
        self.score = self._load()

    def _load(self) -> int:
        """Bando įkelti aukščiausią rezultatą iš failo, jei nepavyksta, grąžina 0."""
        try:
            with open(self.filename, 'r') as f:
                return int(f.read())
        except (IOError, ValueError):
            return 0

    def update(self, new_score: int):
        """Atnaujina aukščiausią rezultatą, jei naujas rezultatas yra didesnis, ir išsaugo jį."""
        if new_score > self.score:
            self.score = new_score
            with open(self.filename, 'w') as f:
                f.write(str(self.score))

    def get(self) -> int:
        """Grąžina dabartinį aukščiausią rezultatą."""
        return self.score

# ------------------------ Pygame Inicializacija -------------------------------
pygame.init()
WIDTH, HEIGHT = 1500, 900
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game")
clock = pygame.time.Clock()

# ---------- Spalvos ----------
WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)
RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
YELLOW  = (255, 255,   0)
CYAN    = (  0, 255, 255)
GREY    = (120, 120, 120)
DARK    = ( 10,  10,  30)
MAGENTA = (255,   0, 255)

# ----------------------- Aukščiausio įvertinimo failo nustatymas ---------------------------
HIGH_SCORE_FILE = "high_score.txt"
hs_manager = HighScoreManager(HIGH_SCORE_FILE)

# =====================================================================
#                               OOP PAGRINDAI
# =====================================================================

class GameObject(pygame.sprite.Sprite):
    """Abstrakti bazinė klasė visiems žaidimo objektams, kurie turi būti piešiami."""
    def __init__(self):
        """Inicializuoja GameObject su numatytu įvaizdžiu ir stačiakampiu."""
        super().__init__()
        self.image: pygame.Surface | None = None
        self.rect: pygame.Rect | None   = None

    def update(self, *args):
        """Atnaujina objektą (implementuojama paveldėtose klasėse)."""
        pass

class Player(GameObject):
    """Žaidėjo laivas: Paveldėjimas, Encapsuliacija, Polimorfizmas."""
    def __init__(self):
        """Inicializuoja žaidėjo laivą su specifiniais atributais (gyvybės, greitis ir kt.)."""
        super().__init__()
        self.image = pygame.Surface((50,40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(25,0),(50,40),(0,40)])
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-10))
        self.speed = 6
        self._health = 5
        self.shield = False
        self.invincible_time = 0
        self.triple_shot_time = 0
        self.big_bullet_time  = 0
        self.speed_buff_time  = 0
        self.multi_shot_time  = 0
        self.shoot_delay_ms = 100
        self._last_shot = pygame.time.get_ticks()

    @property
    def health(self) -> int:
        """Grąžina žaidėjo dabartinę gyvybę."""
        return self._health

    @health.setter
    def health(self, val: int):
        """Nustato žaidėjo gyvybes vertę, ribojant ją tarp 0 ir 20."""
        self._health = max(0, min(20, val))

    def update(self, keys: pygame.key.ScancodeWrapper, *args):
        """Atnaujina žaidėjo poziciją pagal klaviatūros įvestį ir taiko greičio stiprinimus."""
        current_speed = self.speed
        if self.speed_buff_time > 0:
            current_speed *= 1.5  # Padidina greitį 50% (galima koreguoti šį dauginamąjį koeficientą)
        if keys[pygame.K_LEFT]  and self.rect.left  > 0:        self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:    self.rect.x += self.speed
        if keys[pygame.K_UP]    and self.rect.top   > 0:        self.rect.y -= self.speed
        if keys[pygame.K_DOWN]  and self.rect.bottom< HEIGHT:   self.rect.y += self.speed
        for attr in ('invincible_time','triple_shot_time','big_bullet_time',
                     'speed_buff_time','multi_shot_time'):
            t = getattr(self, attr)
            if t: setattr(self, attr, t-1)

    def can_shoot(self) -> bool:
        """Grąžina True, jei žaidėjas gali šaudyti pagal laiko delsą."""
        return pygame.time.get_ticks() - self._last_shot >= self.shoot_delay_ms

    def shoot(self) -> list[GameObject]:
        """Atsižvelgiant į aktyvius galingus šūvius (triple shot, multi shot), šaudo kulkas."""
        self._last_shot = pygame.time.get_ticks()
        big = self.big_bullet_time > 0
        bullets: list[GameObject] = []
        spread = [(-4,-20),(0,-20),(4,-20)] if self.triple_shot_time else [(0,-20)]
        if self.multi_shot_time:
            spread += [(-8,-20),(8,-20)]
        for dx,dy in spread:
            bullets.append(Bullet(self.rect.centerx, self.rect.top, big, dx))
        return bullets

    def take_damage(self, amount: int = 1):
        """Gali paimti žalos taškus, nebent būtų nesunaikinamas arba turi šalmą."""
        if self.invincible_time: return
        if self.shield:
            self.shield = False
        else:
            self._health = max(0, self._health - amount)

    @staticmethod
    def calculate_damage(score: int) -> int:
        """Apskaičiuoja žalos kiekį pagal žaidėjo taškus."""
        if score >= 1000: return 3
        if score >=  500: return 2
        return 1

class Bullet(GameObject):
    """Kulka, kurią šaudo žaidėjas."""
    def __init__(self, x:int, y:int, big:bool=False, dx:int=0):
        """Inicializuoja kulką su pozicija, dydžiu ir greičiu."""
        super().__init__()
        w,h = (12,24) if big else (5,12)
        self.image = pygame.Surface((w,h))
        self.image.fill(YELLOW if big else RED)
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 12 if big else 15
        self.dx = dx

    def update(self,*_):
        """Perkelia kulką aukštyn ir pašalina ją, jei ji išeina už ekrano ribų."""
        self.rect.y -= self.speed
        self.rect.x += self.dx
        if (self.rect.bottom<0 or self.rect.left>WIDTH or
            self.rect.right<0):
            self.kill()

class Enemy(GameObject):
    """Priešo laivas, kuris juda žemyn ir šaudo į žaidėją."""
    def __init__(self, speed:int, health:int):
        """Inicializuoja priešą su greičiu ir gyvybėmis."""
        super().__init__()
        self.image = pygame.Surface((40,32))
        self.image.fill(RED)
        self.rect = self.image.get_rect(
            midtop=(random.randrange(40,WIDTH-40), -40))
        self.speed = speed
        self.health = health
        self.shoot_delay_ms = random.randint(1200,2000)
        self._last_shot = pygame.time.get_ticks()

    def update(self,*_):
        """Perkelia priešą žemyn ir, jei jis išeina už ekrano, grąžina į viršų."""
        self.rect.y += self.speed
        if self.rect.top>HEIGHT:
            self.rect.y = -40

    def take_damage(self, amount:int=1):
        """Sumažina priešų gyvybes pagal žalos dydį."""
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def can_shoot(self):
        """Grąžina True, jei priešas gali šaudyti pagal savo šūvio delsą."""
        return pygame.time.get_ticks() - self._last_shot >= self.shoot_delay_ms

    def shoot(self):
        """Priešas šaudo kulką žemyn."""
        self._last_shot = pygame.time.get_ticks()
        return EnemyBullet(self.rect.centerx, self.rect.bottom)

class EnemyBullet(GameObject):
    """Kulka, kurią šaudo priešai."""
    def __init__(self, x:int, y:int):
        """Inicializuoja priešų kulką su pozicija ir greičiu."""
        super().__init__()
        self.image = pygame.Surface((5,12))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 6

    def update(self,*_):
        """Perkelia kulką žemyn ir pašalina ją, jei ji išeina už ekrano ribų."""
        self.rect.y += self.speed
        if self.rect.top>HEIGHT:
            self.kill()

class Boss(GameObject):
    """Bosso priešas, turintis daugiau gyvybių ir platesnį šūvio modelį."""
    def __init__(self):
        """Inicializuoja bosą su specifiniais atributais (greitis, gyvybės, šūvio delsai)."""
        super().__init__()
        self.image = pygame.Surface((120,120), pygame.SRCALPHA)
        pygame.draw.rect(self.image,RED,(10,10,100,100))
        pygame.draw.circle(self.image,WHITE,(40,40),12)
        pygame.draw.circle(self.image,WHITE,(80,40),12)
        self.rect = self.image.get_rect(center=(WIDTH//2,100))
        self.speed = 2; self._dir = 1; self.health = 100
        self.shoot_delay_ms = 600
        self._last_shot = pygame.time.get_ticks()

    def update(self,*_):
        """Perkelia bosą į kairę ir dešinę pagal ekraną ir keičia kryptį, kai pasiekia ekraną kraštus."""
        self.rect.x += self._dir*self.speed
        if self.rect.left<=0 or self.rect.right>=WIDTH:
            self._dir *= -1

    def take_damage(self, amount:int=10):
        """Sumažina boso gyvybes pagal žalos kiekį."""
        self.health -= amount
        if self.health<=0: self.kill()

    def can_shoot(self):
        """Grąžina True, jei bosas gali šaudyti pagal savo šūvio delsą."""
        return pygame.time.get_ticks() - self._last_shot >= self.shoot_delay_ms

    def shoot(self):
        """Šaudo kulką žemyn nuo boso pozicijos."""
        self._last_shot = pygame.time.get_ticks()
        return EnemyBullet(self.rect.centerx, self.rect.bottom)

class Asteroid(GameObject):
    """Asteroidas, kuris atsitiktinai krenta iš viršaus."""
    def __init__(self):
        """Inicializuoja asteroidą su atsitiktiniu dydžiu ir pozicija."""
        super().__init__()
        r = random.randint(15,30)
        self.image = pygame.Surface((2*r,2*r), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREY, (r,r), r)
        self.rect = self.image.get_rect(
            center=(random.randrange(r,WIDTH-r), -r))
        self.speed = random.randint(2,6)

    def update(self,*_):
        """Perkelia asteroidą žemyn ir pašalina, jei jis išeina už ekrano ribų."""
        self.rect.y += self.speed
        if self.rect.top>HEIGHT:
            self.kill()

class PowerUp(GameObject):
    """Power-up elementas, kurį žaidėjas gali surinkti dėl įvairių naudų."""
    COLOURS = dict(
        triple=BLUE, heal=RED, shield=GREEN,
        big=YELLOW, speed=CYAN,
        invincibility=WHITE, multi=MAGENTA
    )
    def __init__(self, kind:str):
        """Inicializuoja power-up su tipu (triple, heal, shield ir kt.) ir pozicija."""
        super().__init__()
        self.kind = kind; r=12
        self.image = pygame.Surface((2*r,2*r), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.COLOURS[kind], (r,r), r)
        self.rect = self.image.get_rect(
            center=(random.randrange(r,WIDTH-r), -r))
        self.speed = 3
   
    def update(self,*_):
        """Perkelia power-up žemyn ir pašalina jį, jei jis išeina už ekrano ribų."""
        self.rect.y += self.speed
        if self.rect.top>HEIGHT:
            self.kill()

class Explosion(GameObject):
    """Sprogimo efektas, kai objektas sunaikinamas."""
    def __init__(self, x:int, y:int):
        """Inicializuoja sprogimą su pozicija ir gyvavimo laiku."""
        super().__init__()
        self.image = pygame.Surface((10,10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (5,5), 5)
        self.rect = self.image.get_rect(center=(x,y))
        self.lifetime = 10

    def update(self,*_):
        """Sumažina sprogimo gyvavimo laiką ir pašalina, kai jis pasibaigia."""
        self.lifetime -= 1
        if self.lifetime <=0:
            self.kill()

class Menu:
    """Pagrindinis meniu, kuris rodo pavadinimą, instrukcijas ir laukia vartotojo įvesties pradėti žaidimą."""
    def __init__(self):
        """Inicializuoja meniu su skirtingais šriftais ir instrukcijomis."""
        self.font_big   = pygame.font.SysFont(None, 72)  # Pavadinimo šriftas (didelis dydis)
        self.font_medium = pygame.font.SysFont(None, 48)  # Didesnis dydis instrukcijoms
        self.font_small = pygame.font.SysFont(None, 24)  # Įprastas dydis mažam tekstui
        self.instructions = [
            "Valdymas: rodyklės judėti aukštyn, žemyn, kairėn, dešinėn",
            "SPACE šaudyti, P pauzė, ESC išeiti.",
            "Surinkite power-up'us: triple, heal, shield, big, speed, invincibility, multi",
            "Šaudykite į priešų laivus ir rinkite taškus",
            "Jūsų laivas žalias trikampis, priešai raudoni kvadratai",
            "Asteroidai pilki apskritimai, o power-up'ai spalvoti apskritimai",
            "Yra efektai: sprogimas, kai sunaikinamas priešas",
            "Žaidimo pabaiga, kai žaidėjas praranda visas gyvybes",
            "Paspauskite SPACE, kad pradėtumėte!"
        ]
    def display(self):
        """Rodo meniu su pavadinimu ir instrukcijomis."""
        screen.fill(DARK)

        # Pavadinimo tekstas, išcentravimas
        title = self.font_big.render("SPACE SHOOTER", True, WHITE)
        title_x = WIDTH // 2 - title.get_width() // 2  # Išcentravimas horizontaliai
        screen.blit(title, (title_x, 60))  # Padėkite pavadinimą viršuje centre

        # Instrukcijų tekstas išcentravimas
        y_offset = HEIGHT // 2 - (len(self.instructions) * 48) // 2  # Apskaičiuojame vertikalią poziciją centrui
        for line in self.instructions:
            txt = self.font_medium.render(line, True, WHITE)  # Naudojame vidutinį šriftą instrukcijoms
            txt_x = WIDTH // 2 - txt.get_width() // 2  # Išcentravimas kiekvienam eilučių tekstui
            screen.blit(txt, (txt_x, y_offset))
            y_offset += 55  # Tarpas tarp eilučių (didesnis tarpas dėl didesnio teksto)

        pygame.display.flip()

    def countdown(self):
        """Rodo atgalinį skaičiavimą prieš žaidimo pradžią."""
        font = pygame.font.SysFont(None,120)
        for n in (3,2,1):
            screen.fill(DARK)
            txt = font.render(str(n), True, WHITE)
            screen.blit(txt, (WIDTH//2-txt.get_width()//2,
                              HEIGHT//2-txt.get_height()//2))
            pygame.display.flip(); time.sleep(1)

def spawn_enemy_wave(chapter:int,
                     enemy_group:pygame.sprite.Group,
                     all_sprites:pygame.sprite.Group):
    """Sukuria priešų bangą priklausomai nuo dabartinio skyriaus lygio."""
    num = 5 + chapter*2
    for _ in range(num):
        spd = random.randint(1+chapter//2, 3+chapter//2)
        hp  = random.randint(1+chapter//2, 3+chapter//2)
        e = Enemy(spd, hp)
        all_sprites.add(e); enemy_group.add(e)

def game_over_screen(score:int):
    """Rodo žaidimo pabaigos ekraną su galutiniu rezultatu ir pasirinkimu pradėti iš naujo."""
    screen.fill(DARK)
    f_lo = pygame.font.SysFont(None,72)
    go_txt = f_lo.render("GAME OVER", True, WHITE)
    sc_txt = pygame.font.SysFont(None,48).render(f"Score: {score}", True, WHITE)
    re_txt = pygame.font.SysFont(None,32).render("Press SPACE to Restart", True, WHITE)
    screen.blit(go_txt, (WIDTH//2-go_txt.get_width()//2, HEIGHT//4))
    screen.blit(sc_txt, (WIDTH//2-sc_txt.get_width()//2, HEIGHT//2))
    screen.blit(re_txt, (WIDTH//2-re_txt.get_width()//2, HEIGHT//2+50))
    pygame.display.flip()
    waiting=True
    while waiting:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
                waiting=False
        clock.tick(30)

def game_loop() -> bool:
    """Pagrindinis žaidimo ciklas, kuriame vyksta žaidimo veiksmas."""
    chapter, score = 1, 0
    paused = False

    all_s         = pygame.sprite.Group()
    bullets       = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies       = pygame.sprite.Group()
    asteroids     = pygame.sprite.Group()
    buffs         = pygame.sprite.Group()

    player = Player()
    all_s.add(player)
    spawn_enemy_wave(chapter, enemies, all_s)

    while True:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if   ev.key == pygame.K_ESCAPE: return False
                elif ev.key == pygame.K_p:      paused = not paused
                elif ev.key == pygame.K_SPACE and not paused and player.can_shoot():
                    for b in player.shoot():
                        all_s.add(b); bullets.add(b)

        if paused:
            pygame.display.set_caption("Space Shooter – PAUSED")
            continue
        else:
            pygame.display.set_caption("Space Shooter Game")

        # AI priešų šaudymas
        for e in enemies:
            if hasattr(e,'can_shoot') and e.can_shoot():
                eb = e.shoot()
                all_s.add(eb); enemy_bullets.add(eb)

        # Atsitiktiniai atsiradimai
        if random.random() < 0.018:
            a = Asteroid(); all_s.add(a); asteroids.add(a)
        if random.random() < 0.010:
            kind = random.choice(list(PowerUp.COLOURS.keys()))
            p = PowerUp(kind); all_s.add(p); buffs.add(p)

        # atnaujinimai
        keys = pygame.key.get_pressed()
        player.update(keys)
        bullets.update(); enemy_bullets.update()
        enemies.update(); asteroids.update(); buffs.update()

        # kolizijos kulkos→priešai
        for b in bullets:
            hits = pygame.sprite.spritecollide(b, enemies, False)
            for e in hits:
                e.take_damage(2 if player.big_bullet_time else 1)
                b.kill(); score += 10
                all_s.add(Explosion(e.rect.centerx,e.rect.centery))

        # kolizijos žaidėjas→priešai
        collided_enemies = pygame.sprite.spritecollide(player, enemies, False)
        if collided_enemies:
            player.take_damage(1)
        for enemy in collided_enemies:  # Naikina priešą po susidūrimo
            enemy.kill()  # Užtikrina, kad priešas būtų sunaikintas po susidūrimo

        # kolizijos žaidėjas→priešo kulkos
        for eb in pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.take_damage(Player.calculate_damage(score))

        # kolizijos žaidėjas→power-ups
        for p in pygame.sprite.spritecollide(player, buffs, True):
            if   p.kind=='heal': player.health += 2
            elif p.kind=='shield': player.shield = True
            elif p.kind=='big': player.big_bullet_time = 900
            elif p.kind=='speed': player.speed_buff_time = 900
            elif p.kind=='invincibility': player.invincible_time = 900
            elif p.kind=='triple': player.triple_shot_time = 900
            elif p.kind=='multi': player.multi_shot_time = 900

        # kolizijos žaidėjas→asteroidai
        if pygame.sprite.spritecollide(player, asteroids, True):
            player.take_damage(1)

        # kita banga / bosas
        if not enemies:
            chapter += 1
            if chapter % 3 == 0:
                b = Boss(); all_s.add(b); enemies.add(b)
            else:
                spawn_enemy_wave(chapter, enemies, all_s)

        # piešimas
        screen.fill(DARK)
        all_s.draw(screen)
        ui = pygame.font.SysFont(None,28)
        screen.blit(ui.render(f"Score: {score}", True, WHITE), (10,10))
        screen.blit(ui.render(f"Health: {player.health}", True, WHITE), (10,40))
        screen.blit(ui.render(f"High Score: {hs_manager.get()}", True, WHITE), (10,70))
        screen.blit(ui.render(f"Chapter: {chapter}", True, WHITE), (WIDTH-140,10))
        
        # rodyti aktyvius power-up'us
        y_offset = 40
        if player.shield:
            screen.blit(ui.render("Shield Active", True, GREEN), (WIDTH//2 - 70, y_offset))
            y_offset += 30
        if player.triple_shot_time > 0:
            screen.blit(ui.render("Triple Shot Active", True, BLUE), (WIDTH//2 - 70, y_offset))
            y_offset += 30
        if player.big_bullet_time > 0:
            screen.blit(ui.render("Big Bullets Active", True, YELLOW), (WIDTH//2 - 70, y_offset))
            y_offset += 30
        if player.speed_buff_time > 0:
            screen.blit(ui.render("Speed Boost Active", True, CYAN), (WIDTH//2 - 70, y_offset))
            y_offset += 30
        if player.invincible_time > 0:
            screen.blit(ui.render("Invincible Active", True, WHITE), (WIDTH//2 - 70, y_offset))
            y_offset += 30
        if player.multi_shot_time > 0:
            screen.blit(ui.render("Multi-Shot Active", True, MAGENTA), (WIDTH//2 - 70, y_offset))
            y_offset += 30

        pygame.display.flip()

        # žaidimo pabaiga?
        if player.health <= 0:
            hs_manager.update(score)
            game_over_screen(score)
            return True

def main():
    """Pagrindinė žaidimo funkcija, kuri valdo žaidimo meniu ir ciklą."""
    menu = Menu()  # Sukuriama nauja Menu objektas, kad būtų galima rodyti žaidimo meniu
    while True:  # Begalinis ciklas, kuris leidžia žaisti žaidimą tiek kartų, kiek norima
        menu.display()  # Rodo pagrindinį meniu su instrukcijomis ir pavadinimu
        waiting = True  # Kintamasis, kuris nurodo, kad žaidėjas laukia pradėti žaidimą
        while waiting:  # Laukimo ciklas, kol žaidėjas paspaudžia SPACE (pradėti žaidimą)
            for ev in pygame.event.get():  # Tikrinama, ar įvyksta įvykiai (pvz., klavišų paspaudimai)
                if ev.type == pygame.QUIT:  # Jei uždarytas žaidimo langas, išėjimas iš žaidimo
                    pygame.quit(); sys.exit()  # Uždaro Pygame ir baigia programą
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:  # Jei paspaudžiamas SPACE
                    waiting = False  # Nutraukiamas laukimo ciklas, kad žaidimas pradėtųsi
            clock.tick(30)  # Ribojama žaidimo kadrų per sekundę (FPS) iki 30, kad žaidimas nebūtų per greitas
        menu.countdown()  # Rodo atgalinį skaičiavimą (3, 2, 1) prieš pradėdami žaidimą
        if not game_loop():  # Jei žaidimas baigiasi (grąžinama False), nutraukiama žaidimo vykdymo kova
            break  # Išeiname iš pagrindinio ciklo, jei žaidimas baigėsi

    pygame.quit()  # Uždaro Pygame, kai žaidimas baigiasi
    sys.exit()  # Uždaro programą

if __name__ == '__main__':  # Jei šis failas yra vykdomas kaip pagrindinis skriptas
    main()  # Iškviečia pagrindinę funkciją

