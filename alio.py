import pygame
import random
import time
import os
import math
import sys  # Import sys to handle graceful exit in Colab

pygame.init()

# --- Screen Setup ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game")

# --- Colors ---
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY   = (169, 169, 169)
MAGENTA = (255, 0, 255)
CYAN    = (0, 255, 255)

# --- Global Variables ---
high_score = 0
paused = False
chapter = 1
score = 0

# Load saved high score from a file, if exists
if os.path.exists("high_score.txt"):
    with open("high_score.txt", "r") as file:
        high_score = int(file.read())

# -------------------------------
#      CLASS DEFINITIONS
# -------------------------------

class GameObject(pygame.sprite.Sprite):
    """Abstract base class for all game objects. (Abstraction)"""
    def __init__(self):
        super().__init__()
        self.image = None
        self.rect = None
        self.health = 0
        self.speed = 0

    def update(self):
        pass  # Can be overridden by subclasses

class Menu:
    """Simple menu that displays 'Press ENTER to start'."""
    def __init__(self):
        self.font = pygame.font.SysFont(None, 48)

    def display(self):
        screen.fill(BLACK)
        title_text = self.font.render("SPACE SHOOTER GAME", True, WHITE)
        info_text = self.font.render("Press ENTER to Start", True, WHITE)

        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(info_text,  (WIDTH//2 - info_text.get_width()//2,  HEIGHT//2))
        pygame.display.flip()

class Player(GameObject):
    """Player class, inherits from GameObject (Inheritance)"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5
        self._health = 1  # Encapsulation: private attribute for health
        self.shield = False
        self.invincible_time = 0
        self.laser_mode = False

    @property
    def health(self):
        """Encapsulation: Property method for health."""
        return self._health

    @health.setter
    def health(self, value):
        if value < 0:
            self._health = 0
        else:
            self._health = value

    def update(self, keys):
        # Movement logic (Polymorphism: Player behavior)
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

        # Decrement invincibility timer
        if self.invincible_time > 0:
            self.invincible_time -= 1

    def shoot(self):
        """Polymorphism: Player can shoot differently based on power-ups."""
        if self.laser_mode:
            return Laser(self.rect.centerx, self.rect.top)
        else:
            return Bullet(self.rect.centerx, self.rect.top)

    def take_damage(self, amount=1):
        """Reduce player health unless invincible or shielded."""
        if self.invincible_time > 0:
            return  # Invincible -> ignore damage
        if self.shield:
            self.shield = False
            return
        self.health -= amount

class Bullet(GameObject):
    """Bullet class, inherits from GameObject (Inheritance)"""
    def __init__(self, x, y, is_supercharged=False):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED if not is_supercharged else YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7 if not is_supercharged else 15
        self.is_supercharged = is_supercharged

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Laser(GameObject):
    """Laser class (Inheritance from GameObject)"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 15

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(GameObject):
    """Generic enemy (Inheritance)"""
    def __init__(self, speed, health, color=RED):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = speed
        self.health = health

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def shoot(self):
        """Different shooting logic for enemy (Polymorphism)."""
        return EnemyBullet(self.rect.centerx, self.rect.bottom)

class EnemyBullet(GameObject):
    """A bullet shot by an enemy or boss (Inheritance)"""
    def __init__(self, x, y, speed=5):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class PowerUp(GameObject):
    """Floating power-up sprite (Inheritance)"""
    def __init__(self, buff_type):
        super().__init__()
        self.buff_type = buff_type
        # Just color-code them for illustration
        color = WHITE
        if buff_type == 'invincibility':
            color = MAGENTA
        elif buff_type == 'shield':
            color = BLUE
        elif buff_type == 'laser':
            color = YELLOW

        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-60, -30)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Asteroid(GameObject):
    """Simple asteroid that falls from top to bottom."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class CircularBoss(GameObject):
    """Boss that moves in a circular pattern."""
    def __init__(self, all_sprites, enemies, enemy_bullets):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(MAGENTA)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 3
        self.angle = 0
        self.all_sprites = all_sprites
        self.enemies = enemies
        self.enemy_bullets = enemy_bullets
        self.health = 10

    def update(self):
        # Move the boss in a circular pattern
        self.angle += 0.1
        self.rect.centerx = WIDTH // 2 + 100 * math.cos(self.angle)
        self.rect.centery = HEIGHT // 2 + 100 * math.sin(self.angle)

        # Shoot bullets
        if random.random() < 0.05:
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery)
            self.enemy_bullets.add(bullet)
            self.all_sprites.add(bullet)

        # Check for collisions with player
        if pygame.sprite.collide_rect(self, player):
            player.take_damage()

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()

class MinionSummonerBoss(GameObject):
    """Boss that summons minions."""
    def __init__(self, all_sprites, enemies, enemy_bullets):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.health = 15
        self.all_sprites = all_sprites
        self.enemies = enemies
        self.enemy_bullets = enemy_bullets

    def update(self):
        # Summon minions (regular enemies)
        if random.random() < 0.1:
            speed = random.randint(1, 3)
            health = random.randint(1, 3)
            enemy = Enemy(speed, health)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Shoot bullets
        if random.random() < 0.05:
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery)
            self.enemy_bullets.add(bullet)
            self.all_sprites.add(bullet)

        # Check for collisions with player
        if pygame.sprite.collide_rect(self, player):
            player.take_damage()

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()

# -----------------------------
#       GAME FUNCTIONS
# -----------------------------

def save_high_score(score):
    """Save high score to a file."""
    global high_score
    if score > high_score:
        high_score = score
        with open("high_score.txt", "w") as file:
            file.write(str(high_score))

def spawn_enemies(chapter, enemies_group, all_sprites):
    """Spawn a batch of regular enemies based on chapter."""
    num_enemies = 5 + chapter * 2
    for _ in range(num_enemies):
        speed = random.randint(1 + chapter // 2, 3 + chapter // 2)
        health = random.randint(1 + chapter // 2, 3 + chapter // 2)
        enemy = Enemy(speed, health)
        all_sprites.add(enemy)
        enemies_group.add(enemy)

def spawn_buffs(buffs_group, all_sprites):
    """Spawn a power-up with 20% chance."""
    if random.random() < 0.2:
        buff_type = random.choice(['invincibility', 'shield', 'laser'])
        buff = PowerUp(buff_type)
        all_sprites.add(buff)
        buffs_group.add(buff)

def spawn_asteroids(asteroids_group, all_sprites):
    """Spawn an asteroid with 10% chance."""
    if random.random() < 0.1:
        asteroid = Asteroid()
        all_sprites.add(asteroid)
        asteroids_group.add(asteroid)

def pause_menu():
    """Pause screen; resumes on 'P' key press."""
    global paused
    font = pygame.font.SysFont(None, 48)
    pause_text = font.render("Paused - Press P to Continue", True, WHITE)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Resume game when P is pressed
                    paused = False

# --- Main Function ---
def main():
    """Main function: shows menu, starts game loop."""
    global chapter, score, high_score, paused

    menu = Menu()
    running = True
    clock = pygame.time.Clock()

    # Show start menu until we press ENTER
    while running:
        menu.display()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = game_loop(clock)  # starts the game
    pygame.quit()

def game_loop(clock):
    """Single 'run' of the game. Returns False if the player dies or quits."""
    global chapter, score, high_score, paused

    # Reset chapter & score for a fresh game each time
    chapter = 1
    score = 0

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    buffs = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    # Create player
    player = Player()  # Create the player object here
    all_sprites.add(player)  # Add player to the sprite group

    # Spawn initial enemies/buffs/asteroids
    spawn_enemies(chapter, enemies, all_sprites)
    spawn_buffs(buffs, all_sprites)
    spawn_asteroids(asteroids, all_sprites)

    running = True

    # --- START TIME FOR TIMEOUT ---
    start_time = time.time()
    limit_seconds = 10  # For example, end game automatically in 10 seconds

    while running:
        clock.tick(60)
        # If we've been running for more than limit_seconds, break out
        if time.time() - start_time > limit_seconds:
            print("Time limit reached. Exiting game loop for Colab.")
            running = False

        # The rest of your loop remains the same:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = player.shoot()  # Now player is defined
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                elif event.key == pygame.K_p:
                    paused = True
                    pause_menu()

        if paused:
            continue

        keys = pygame.key.get_pressed()
        all_sprites.update(keys)

        # Bullet-enemy collisions
        for bullet in bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                enemy.take_damage()
                score += 10
                bullet.kill()

        # Enemy-player collisions
        for enemy in enemies:
            if pygame.sprite.collide_rect(enemy, player):  # Ensure player is defined
                player.take_damage()
                enemy.kill()

        # Enemy bullet collisions
        for bullet in enemy_bullets:
            if pygame.sprite.collide_rect(bullet, player):  # Ensure player is defined
                player.take_damage()
                bullet.kill()

        # Asteroid collisions
        for asteroid in asteroids:
            if pygame.sprite.collide_rect(asteroid, player):  # Ensure player is defined
                player.take_damage()
                asteroid.kill()

        # Power-up pickups
        powerup_hits = pygame.sprite.spritecollide(player, buffs, True)
        for buff in powerup_hits:
            if buff.buff_type == 'invincibility':
                player.invincible_time = 300  # ~5 seconds at 60 FPS
            elif buff.buff_type == 'shield':
                player.shield = True
            elif buff.buff_type == 'laser':
                player.laser_mode = True

        # ---------------------------------------------------
        # Check if wave/boss is cleared -> move to next chapter
        # ---------------------------------------------------
        if len(enemies) == 0:
            chapter += 1

            # If we beat the final chapter (6), you win
            if chapter > 6:
                font = pygame.font.SysFont(None, 36)
                win_text = font.render("YOU WIN!", True, (0, 200, 0))
                screen.blit(win_text, (WIDTH // 2 - 50, HEIGHT // 2))
                pygame.display.flip()
                save_high_score(score)
                time.sleep(3)
                return False

            # If new wave is a boss
            if chapter % 3 == 0:
                if chapter % 2 == 0:
                    boss = CircularBoss(all_sprites, enemies, enemy_bullets)
                else:
                    boss = MinionSummonerBoss(all_sprites, enemies, enemy_bullets)
                all_sprites.add(boss)
                enemies.add(boss)
            else:
                # Normal wave
                spawn_enemies(chapter, enemies, all_sprites)
                spawn_buffs(buffs, all_sprites)
                spawn_asteroids(asteroids, all_sprites)

        # -- DRAW --
        all_sprites.draw(screen)

        # Display score/health/high score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))
        screen.blit(high_score_text, (WIDTH - 200, 10))

        # Check game over (single hit = death if we run out of health)
        if player.health <= 0:
            save_high_score(score)
            game_over_text = font.render("GAME OVER!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.flip()
            time.sleep(2)
            return False

        pygame.display.flip()

    pygame.quit()
    sys.exit()  # Exit gracefully

if __name__ == "__main__":
    main()
