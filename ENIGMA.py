# main.py
from typing import Self
import pygame
import random
import math
import os
from math import *

# --- Настройки ---
WIDTH, HEIGHT = 2560, 1440
FPS = 60
ASSETS = "assets"
IMAGES_SUBDIR = "imag"   
MUSIC_SUBDIR = "music"

# --- Инициализация ---
pygame.init()
try:
    mixer.init()
except Exception:
    
    mixer = None

screen = pygame.display.set_mode((WIDTH, HEIGHT))
window=pygame.display.set_mode((2560, 1440))
pygame.display.set_caption("ENIGMA")
clock = pygame.time.Clock()


basedir = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
imagesdir = os.path.join(basedir, ASSETS, IMAGES_SUBDIR)
musicdir = os.path.join(basedir, ASSETS, MUSIC_SUBDIR)

def safe_load_image(path, fallback_size=(32, 32)):
    """Загружает изображение, если нет — возвращает заметную поверхность-заглушку."""
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return img
        except Exception:
            pass
    surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
    surf.fill((200, 0, 200))  
    return surf

def load_sound(name):
    """Возвращает Sound или None (без аварийного завершения)."""
    if mixer is None:
        return None
    path = os.path.join(musicdir, name)
    if os.path.exists(path):
        try:
            return mixer.Sound(path)
        except Exception:
            return None
    return None


bg_img = safe_load_image(os.path.join(imagesdir, "room.png"), fallback_size=(WIDTH, HEIGHT))
enemy_img = safe_load_image(os.path.join(imagesdir, "enemy.png"), fallback_size=(48, 48))
jumpscare_img = safe_load_image(os.path.join(imagesdir, "jumpscare.png"), fallback_size=(WIDTH, HEIGHT))
player_img = safe_load_image(os.path.join(imagesdir, "player.png"), fallback_size=(40, 40))
player_img2 = safe_load_image(os.path.join(imagesdir, "me.png"), fallback_size=(40, 40))
enemy_img2 = safe_load_image(os.path.join(imagesdir, "thiswasnotme.png"), fallback_size=(40, 40))
bg_img2 = safe_load_image(os.path.join(imagesdir, "whyyouthere.png"), fallback_size=(48, 48))

ambient = load_sound("ambient.wav")
heartbeat = load_sound("heartbeat.wav")
if ambient:
    try:
        ambient.set_volume(0.4)
        ambient.play(loops=-1)
    except Exception:
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.orig = random.choice([player_img, player_img2])
        self.image = self.orig
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 180.0  # px/s

    def update(self, dt, keys):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        if keys[pygame.K_f]:  # быстрое завершение (F)
            pygame.quit()
            raise SystemExit

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            if length != 0:
                dx /= length
                dy /= length
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt
        
        self.rect.clamp_ip(screen.get_rect())

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice([enemy_img, enemy_img2])
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 70.0
        self.alert = False

    def update(self, dt, target_pos):
        tx, ty = target_pos
        ex, ey = self.rect.center
        dx, dy = tx - ex, ty - ey
        dist = math.hypot(dx, dy)
        if dist > 5:
            dx /= dist
            dy /= dist
            multiplier = 1.6 if self.alert else 1.0
            move = self.speed * multiplier * dt
            self.rect.x += dx * move
            self.rect.y += dy * move


player = Player(WIDTH // 2, HEIGHT // 2)
enemy = Enemy(100, 100)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemy)



def make_flashlight_mask(center, radius=180, angle_deg=80, direction=(1, 0)):
    mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    mask.fill((0, 0, 0, 220))
    cx, cy = center
    dx, dy = direction
    base_angle = math.atan2(dy, dx)
    half = math.radians(angle_deg / 2)
    left = (cx + math.cos(base_angle - half) * radius, cy + math.sin(base_angle - half) * radius)
    right = (cx + math.cos(base_angle + half) * radius, cy + math.sin(base_angle + half) * radius)
   
    pygame.draw.polygon(mask, (0, 0, 0, 0), [(cx, cy), left, right])
    
    circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(circle, (0, 0, 0, 0), (radius, radius), radius)
    mask.blit(circle, (int(cx - radius), int(cy - radius)), special_flags=pygame.BLEND_RGBA_MIN)
    return mask


flicker_timer = 0.0
flicker_state = 1.0  


heartbeat_timer = 0.0
heartbeat_cooldown = 0.0
scare_mode = False
scare_timer = 0.0


running = True
last_time = pygame.time.get_ticks() / 1000.0

font = pygame.font.SysFont(None, 20)

while running:
    now = pygame.time.get_ticks() / 1000.0
    dt = now - last_time
    
    if dt > 0.1:
        dt = 0.1
    last_time = now

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()
   
    player.update(dt, keys)
    enemy.update(dt, player.rect.center)
    def update(self, dt, target_pos):
        try:
            tx, ty = target_pos
        except:
            return  # если передали мусор — просто пропускаем кадр

        ex, ey = self.rect.center
        dx = float(tx - ex)
        dy = float(ty - ey)

        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        dx /= dist
        dy /= dist

        multiplier = 1.6 if self.alert else 1.0
        move = self.speed * multiplier * dt

        self.rect.x += dx * move
        self.rect.y += dy * move

    
    flicker_timer += dt
    if flicker_timer > 0.12:
        
        if random.random() > 0.92:
            flicker_state = random.uniform(0.05, 0.25)
        else:
            flicker_state = random.uniform(0.7, 1.0)
        flicker_timer = 0.0

   
    dist = math.hypot(enemy.rect.centerx - player.rect.centerx, enemy.rect.centery - player.rect.centery)

   
    if dist < 120:
        heartbeat_timer += dt
        if heartbeat_timer > 0.8 and heartbeat and heartbeat_cooldown <= 0:
            try:
                heartbeat.play()
            except Exception:
                pass
            heartbeat_cooldown = 1.2
            heartbeat_timer = 0.0
        if dist < 70 and random.random() < 0.008:
            scare_mode = True
            scare_timer = 1.0
            if heartbeat:
                try:
                    heartbeat.play()
                except Exception:
                    pass
    if heartbeat_cooldown > 0:
        heartbeat_cooldown -= dt

    
    enemy.alert = dist < 220

    screen.fill((0, 0, 0))
    screen.blit(random.choice([bg_img,bg_img]), (0, 0))

   
    screen.blit(enemy.image, enemy.rect)
    screen.blit(player.image, player.rect)

   
    mouse_pos = pygame.mouse.get_pos()
    dir_to_mouse = (mouse_pos[0] - player.rect.centerx, mouse_pos[1] - player.rect.centery)
    dir_len = math.hypot(*dir_to_mouse)
    if dir_len == 0:
        dir_vec_norm = (1.0, 0.0)
    else:
        dir_vec_norm = (dir_to_mouse[0] / dir_len, dir_to_mouse[1] / dir_len)

    
    radius = int(250 * max(0.05, flicker_state))
    mask = make_flashlight_mask(player.rect.center, radius=radius, angle_deg=80, direction=dir_vec_norm)
    screen.blit(mask, (0, 0))
    


    txt = font.render("WASD / Arrows — движение. F — выйти.", True, (200, 200, 200))
    screen.blit(txt, (8, HEIGHT - 26))

    
    if scare_mode:
        screen.blit(pygame.transform.scale(jumpscare_img, (WIDTH, HEIGHT)), (0, 0))
        scare_timer -= dt
        if scare_timer <= 0:
            scare_mode = False

    scaled_surface=pygame.transform.scale(screen, (2560, 1440))
    window.blit(scaled_surface, (0, 0))
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()