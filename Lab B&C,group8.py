#!/usr/init/env python3
# -*- coding: utf-8 -*-
"""
PSB Roman Battle Game - Mythic Clash (Ultimate Engine Edition - Group 08)
Assignment: Introduction to Programming (ITGP2008) - PSB Academy
Features: Canvas 2D UI, Procedural Sound Synthesis, Dynamic Skills, Cooldowns,
          Status Effects, Floating Combat Numbers, Particle Physics, Screen Shake, 
          Smart AI Logic, Event Logging, & Group 08 Documentation Modal.
"""

import pygame
import random
import os
import math
from datetime import datetime

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Screen Configuration
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PSB Roman Battle Game - Mythic Clash [Ultimate Edition]")

# Color Palette (Canvas 2D Aesthetic)
BG_COLOR = (18, 18, 28)
PANEL_BG = (28, 30, 48)
PANEL_BORDER = (60, 65, 95)
WHITE = (255, 255, 255)
BLACK = (10, 10, 15)
RED = (230, 60, 60)
GREEN = (50, 200, 100)
BLUE = (60, 130, 240)
GOLD = (240, 185, 40)
GRAY = (150, 150, 170)
SHIELD_COLOR = (80, 180, 250)
BURN_COLOR = (250, 120, 40)

# Fonts
font = pygame.font.SysFont("Arial", 18)
font_bold = pygame.font.SysFont("Arial", 18, bold=True)
large_font = pygame.font.SysFont("Arial", 24, bold=True)
title_font = pygame.font.SysFont("Arial", 28, bold=True)

# Ensure Asset Directories Exist
os.makedirs('assets/art', exist_ok=True)
os.makedirs('assets/audio', exist_ok=True)

def load_image(name, scale=None):
    fullname = os.path.join('assets/art', name)
    if os.path.exists(fullname):
        try:
            image = pygame.image.load(fullname)
            if scale:
                image = pygame.transform.scale(image, scale)
            return image
        except:
            pass
    return None

unit_size = (64, 64)
unit_images = {
    "Jupiter": load_image('jupiter.png', unit_size),
    "Mars": load_image('mars.png', unit_size),
    "Minerva": load_image('minerva.png', unit_size),
    "AI87": load_image('pluto.png', unit_size),
    "AI42": load_image('neptune.png', unit_size),
    "AI95": load_image('vulcan.png', unit_size)
}

# --- Event Logger (Member 4 Responsibility) ---
def log_game_event(event_description):
    """Records all game events with timestamps into a plain text file."""
    try:
        with open("game_event_log.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {event_description}\n")
    except Exception:
        pass

# --- Web Audio API Alternative (Procedural Sound Synthesis) ---
def play_synth_sound(sound_type):
    """Generates procedural sound effects dynamically using Pygame mixer buffer."""
    try:
        sample_rate = 22050
        duration = 0.15
        if sound_type == "hit":
            freq = 150
        elif sound_type == "buff":
            freq = 440
        elif sound_type == "win":
            freq = 587
        else:
            freq = 220

        num_samples = int(sample_rate * duration)
        buffer = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            value = int(127 * math.sin(2 * math.pi * freq * t) * max(0, (1 - i / num_samples)))
            buffer.append(max(0, min(255, value + 128)))
            
        sound = pygame.mixer.Sound(buffer=bytes(buffer))
        sound.set_volume(0.3)
        sound.play()
    except Exception:
        pass

# --- Visual Effects & Mechanics ---
class ScreenShake:
    def __init__(self):
        self.timer = 0
        self.intensity = 0

    def trigger(self, duration, intensity):
        self.timer = duration
        self.intensity = intensity

    def get_offset(self):
        if self.timer > 0:
            self.timer -= 1
            return (random.randint(-self.intensity, self.intensity),
                    random.randint(-self.intensity, self.intensity))
        return (0, 0)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 40)
        self.size = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surf, offset):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x + offset[0]), int(self.y + offset[1])), int(self.size))

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 45
        self.vy = -1.5

    def update(self):
        self.y += self.vy
        self.life -= 1

    def draw(self, surf, offset):
        if self.life > 0:
            txt_surface = font_bold.render(self.text, True, self.color)
            surf.blit(txt_surface, (int(self.x + offset[0]), int(self.y + offset[1])))

class Skill:
    def __init__(self, name, mana_cost, cooldown, description, action_type, power):
        self.name = name
        self.mana_cost = mana_cost
        self.max_cooldown = cooldown
        self.current_cooldown = 0
        self.description = description
        self.action_type = action_type  # 'attack', 'buff', 'heal'
        self.power = power

class Unit:
    def __init__(self, name, hp, atk, def_p, profession):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.def_p = def_p
        self.profession = profession
        self.level = 1
        self.exp = 0
        self.shield = 0
        self.burn_turns = 0
        self.skills = [
            Skill("Basic Strike", 0, 0, "Standard melee attack", "attack", 1.0),
            Skill("Heavy Slash", 10, 2, "High damage strike (1.5x ATK)", "attack", 1.5),
            Skill("Divine Shield", 15, 3, "Boosts defense by +10 shield", "buff", 10)
        ]

    def update_status(self):
        if self.burn_turns > 0:
            self.hp -= 8
            self.burn_turns -= 1
            if self.hp < 0: 
                self.hp = 0
        for s in self.skills:
            if s.current_cooldown > 0:
                s.current_cooldown -= 1

    def attack_target(self, target, skill_idx=0):
        """Combat calculation based on PSB Assignment Rules + Dynamic Skills & Status Effects[cite: 16]:
           Damage = attacker.ATK - (target.DEF + random between -5 to 10)
        """
        skill = self.skills[skill_idx]
        skill.current_cooldown = skill.max_cooldown

        if skill.action_type == 'buff':
            self.shield += skill.power
            return 0, False, f"{self.name} used {skill.name}, gaining +{int(skill.power)} Shield!"

        def_variance = random.randint(-5, 10)
        raw_dmg = int(self.atk * skill.power) - (target.def_p + def_variance)
        
        if target.shield > 0:
            absorbed = min(target.shield, raw_dmg if raw_dmg > 0 else 0)
            target.shield -= absorbed
            raw_dmg -= absorbed

        dmg = raw_dmg if raw_dmg > 0 else 0
        target.hp -= dmg
        if target.hp < 0:
            target.hp = 0

        # EXP Calculation & Rules[cite: 16]
        self.exp += dmg
        target.exp += self.def_p

        if dmg > 10:
            self.exp += int(dmg * 0.2)  # +20% extra EXP
        elif dmg <= 0:
            self.exp += int(self.atk * 0.5)  # +50% extra EXP

        # Level Up / Promotion Check (Threshold: 100 EXP)[cite: 16]
        leveled_up = False
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            leveled_up = True

        msg = f"{self.name} used {skill.name} on {target.name} for {dmg} damage!"
        return dmg, leveled_up, msg

# --- Initialize Teams (Member 1 & 2) ---
player_units = [
    Unit("Jupiter", 100, 18, 6, "Warrior"),
    Unit("Mars", 100, 20, 5, "Warrior"),
    Unit("Minerva", 100, 8, 12, "Tanker")
]

ai_units = [
    Unit("AI87", 100, 16, 8, "Tanker"),
    Unit("AI42", 100, 19, 6, "Warrior"),
    Unit("AI95", 100, 7, 14, "Tanker")
]

selected_player_idx = 0
selected_skill_idx = 0
turn = "player"
game_message = "Select Hero & Skill on left, then click an Enemy target to attack!"
show_docs_modal = False

shake = ScreenShake()
particles = []
floating_texts = []

# Game Loop Initialization
log_game_event("Game initialized. PSB Roman Battle Game (Ultimate Edition) started.")
running = True
clock = pygame.time.Clock()

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                show_docs_modal = not show_docs_modal
            elif event.key == pygame.K_1:
                selected_skill_idx = 0
            elif event.key == pygame.K_2:
                selected_skill_idx = 1
            elif event.key == pygame.K_3:
                selected_skill_idx = 2

        elif event.type == pygame.MOUSEBUTTONDOWN and not show_docs_modal:
            # Check Click on Player Units (Hero Selection)
            p_y = 100
            for i, p in enumerate(player_units):
                rect = pygame.Rect(50, p_y, 280, 85)
                if rect.collidepoint(mouse_pos) and p.hp > 0:
                    selected_player_idx = i
                    game_message = f"Selected {p.name}. Choose a skill or click enemy."
                p_y += 105

            # Check Click on Skill Buttons
            s_x = 360
            for idx, skill in enumerate(player_units[selected_player_idx].skills):
                s_rect = pygame.Rect(s_x, 530, 110, 35)
                if s_rect.collidepoint(mouse_pos):
                    if skill.current_cooldown == 0:
                        selected_skill_idx = idx
                        game_message = f"Selected Skill: {skill.name}"
                    else:
                        game_message = f"Skill {skill.name} is on cooldown ({skill.current_cooldown} turns)!"
                s_x += 120

            # Check Click on AI Units (Target Selection for Player Turn - Member 3)
            if turn == "player":
                ai_y = 100
                for j, a in enumerate(ai_units):
                    e_rect = pygame.Rect(670, ai_y, 280, 85)
                    if e_rect.collidepoint(mouse_pos):
                        active_p = player_units[selected_player_idx]
                        active_skill = active_p.skills[selected_skill_idx]

                        if active_p.hp <= 0:
                            game_message = "Selected hero is defeated! Choose another living hero."
                        elif a.hp <= 0:
                            game_message = "Target is already defeated! Choose another enemy."
                        elif active_skill.current_cooldown > 0:
                            game_message = f"Skill {active_skill.name} is on cooldown!"
                        else:
                            # Execute Skill & Apply Formulas
                            dmg, leveled, msg = active_p.attack_target(a, selected_skill_idx)
                            if leveled:
                                msg += f" {active_p.name} Promoted to Lvl {active_p.level}!"
                            game_message = msg
                            log_game_event(msg)

                            if active_skill.action_type == 'buff':
                                play_synth_sound("buff")
                            else:
                                play_synth_sound("hit")
                                shake.trigger(12, 6)
                                for _ in range(18):
                                    particles.append(Particle(e_rect.centerx, e_rect.centery, RED))
                                floating_texts.append(FloatingText(e_rect.centerx, e_rect.centery - 20, f"-{dmg}", GOLD))

                            # Check Win condition[cite: 15]
                            if all(enemy.hp <= 0 for enemy in ai_units):
                                game_message = "Victory! Player team destroyed all opponent units!"
                                log_game_event("Victory! Player team won the game.")
                                play_synth_sound("win")
                                turn = "game_over"
                            elif a.hp <= 0:
                                log_game_event(f"{a.name} was defeated and removed from team.")
                                turn = "ai"
                            else:
                                turn = "ai"
                    ai_y += 105

            # Check Click on Docs Button
            docs_btn = pygame.Rect(820, 20, 140, 35)
            if docs_btn.collidepoint(mouse_pos):
                show_docs_modal = not show_docs_modal

    # --- AI Turn Logic (Smart AI Decision Making - Member 4) ---
    if turn == "ai" and not show_docs_modal:
        pygame.time.delay(700)
        alive_ais = [a for a in ai_units if a.hp > 0]
        alive_players = [p for p in player_units if p.hp > 0]

        if alive_ais and alive_players:
            active_ai = random.choice(alive_ais)
            target_p = random.choice(alive_players)
            
            # Smart AI: 70% basic/heavy attack, 30% shield buff if ready
            ai_skill_idx = 0
            if active_ai.skills[2].current_cooldown == 0 and random.random() < 0.3:
                ai_skill_idx = 2
            elif active_ai.skills[1].current_cooldown == 0 and random.random() < 0.5:
                ai_skill_idx = 1

            dmg, leveled, ai_msg = active_ai.attack_target(target_p, ai_skill_idx)
            if leveled:
                ai_msg += f" {active_ai.name} Promoted to Lvl {active_ai.level}!"
            game_message += f" | {ai_msg}"
            log_game_event(ai_msg)

            if active_ai.skills[ai_skill_idx].action_type == 'buff':
                play_synth_sound("buff")
            else:
                play_synth_sound("hit")
                shake.trigger(8, 4)
                for _ in range(15):
                    particles.append(Particle(150, 200, RED))
                floating_texts.append(FloatingText(150, 180, f"-{dmg}" if dmg > 0 else "BUFF", RED))

            active_ai.update_status()
            
            if all(p.hp <= 0 for p in player_units):
                game_message = "Defeat! AI team destroyed all your units!"
                log_game_event("Defeat! AI team won the game.")
                turn = "game_over"
            else:
                turn = "player"

    # Update particles and floating numbers
    for p in particles[:]:
        p.update()
        if p.life <= 0: particles.remove(p)
    for ft in floating_texts[:]:
        ft.update()
        if ft.life <= 0: floating_texts.remove(ft)

    # --- Rendering UI (Canvas 2D Style - Member 5) ---
    offset = shake.get_offset()
    screen.fill(BG_COLOR)

    # Title Bar
    title_surf = title_font.render("PSB Roman Battle Game - Mythic Clash", True, GOLD)
    screen.blit(title_surf, (50 + offset[0], 20 + offset[1]))

    # Docs Button
    docs_rect = pygame.Rect(820 + offset[0], 20 + offset[1], 140, 35)
    pygame.draw.rect(screen, PANEL_BORDER, docs_rect, 0, 6)
    docs_txt = font_bold.render("Group 08 Docs", True, WHITE)
    screen.blit(docs_txt, (docs_rect.x + 15, docs_rect.y + 7))

    # --- Draw Player Cards (Left) ---
    p_y = 100
    for i, p in enumerate(player_units):
        rect = pygame.Rect(50 + offset[0], p_y + offset[1], 280, 85)
        border_col = GREEN if i == selected_player_idx else PANEL_BORDER
        if p.hp <= 0: border_col = RED

        pygame.draw.rect(screen, PANEL_BG, rect, 0, 8)
        pygame.draw.rect(screen, border_col, rect, 2, 8)

        if p.name in unit_images and unit_images[p.name]:
            screen.blit(unit_images[p.name], (rect.x + 10, rect.y + 10))
        else:
            pygame.draw.rect(screen, BLUE, (rect.x + 10, rect.y + 10, 64, 64), 0, 6)

        name_txt = font_bold.render(f"{p.name} ({p.profession})", True, WHITE if p.hp > 0 else GRAY)
        screen.blit(name_txt, (rect.x + 85, rect.y + 8))

        # HP Bar
        pygame.draw.rect(screen, BLACK, (rect.x + 85, rect.y + 32, 175, 12), 0, 4)
        hp_ratio = max(0, p.hp / p.max_hp)
        pygame.draw.rect(screen, GREEN if p.hp > 0 else RED, (rect.x + 85, rect.y + 32, int(175 * hp_ratio), 12), 0, 4)
        hp_lbl = font.render(f"HP: {p.hp}/100", True, WHITE)
        screen.blit(hp_lbl, (rect.x + 88, rect.y + 30))

        # Status & Shield info
        stat_str = f"Shield: {p.shield}" if p.shield > 0 else f"Lvl: {p.level} | EXP: {p.exp}"
        stat_lbl = font.render(stat_str, True, SHIELD_COLOR if p.shield > 0 else GOLD)
        screen.blit(stat_lbl, (rect.x + 85, rect.y + 52))

        p_y += 105

    # --- Draw AI Cards (Right) ---
    ai_y = 100
    for i, a in enumerate(ai_units):
        rect = pygame.Rect(670 + offset[0], ai_y + offset[1], 280, 85)
        border_col = RED if a.hp > 0 else PANEL_BORDER

        pygame.draw.rect(screen, PANEL_BG, rect, 0, 8)
        pygame.draw.rect(screen, border_col, rect, 2, 8)

        if a.name in unit_images and unit_images[a.name]:
            screen.blit(unit_images[a.name], (rect.x + 10, rect.y + 10))
        else:
            pygame.draw.rect(screen, RED, (rect.x + 10, rect.y + 10, 64, 64), 0, 6)

        name_txt = font_bold.render(f"{a.name} ({a.profession})", True, WHITE if a.hp > 0 else GRAY)
        screen.blit(name_txt, (rect.x + 85, rect.y + 8))

        pygame.draw.rect(screen, BLACK, (rect.x + 85, rect.y + 32, 175, 12), 0, 4)
        hp_ratio = max(0, a.hp / a.max_hp)
        pygame.draw.rect(screen, RED if a.hp > 0 else GRAY, (rect.x + 85, rect.y + 32, int(175 * hp_ratio), 12), 0, 4)
        hp_lbl = font.render(f"HP: {a.hp}/100", True, WHITE)
        screen.blit(hp_lbl, (rect.x + 88, rect.y + 30))

        stat_str = f"Shield: {a.shield}" if a.shield > 0 else f"Lvl: {a.level} | EXP: {a.exp}"
        stat_lbl = font.render(stat_str, True, SHIELD_COLOR if a.shield > 0 else GOLD)
        screen.blit(stat_lbl, (rect.x + 85, rect.y + 52))

        ai_y += 105

    # --- Dynamic Skills Panel (Bottom Center) ---
    skills_bg = pygame.Rect(350 + offset[0], 480 + offset[1], 300, 120)
    pygame.draw.rect(screen, PANEL_BG, skills_bg, 0, 10)
    pygame.draw.rect(screen, PANEL_BORDER, skills_bg, 2, 10)

    active_hero = player_units[selected_player_idx]
    s_title = font_bold.render(f"Skills: {active_hero.name}", True, GOLD)
    screen.blit(s_title, (skills_bg.x + 15, skills_bg.y + 10))

    s_x = skills_bg.x + 15
    for idx, skill in enumerate(active_hero.skills):
        s_rect = pygame.Rect(s_x, skills_bg.y + 40, 85, 65)
        is_selected = (idx == selected_skill_idx)
        btn_border = GOLD if is_selected else PANEL_BORDER
        pygame.draw.rect(screen, (40, 45, 70), s_rect, 0, 6)
        pygame.draw.rect(screen, btn_border, s_rect, 2, 6)

        stxt = font_bold.render(skill.name.split()[0], True, WHITE)
        screen.blit(stxt, (s_rect.x + 8, s_rect.y + 12))
        
        cd_str = f"CD: {skill.current_cooldown}" if skill.current_cooldown > 0 else "Ready"
        cd_col = RED if skill.current_cooldown > 0 else GREEN
        cd_txt = font.render(cd_str, True, cd_col)
        screen.blit(cd_txt, (s_rect.x + 10, s_rect.y + 38))

        s_x += 95

    # --- Game Log Message Box ---
    log_rect = pygame.Rect(50 + offset[0], 615 + offset[1], 900, 50)
    pygame.draw.rect(screen, PANEL_BG, log_rect, 0, 6)
    pygame.draw.rect(screen, PANEL_BORDER, log_rect, 1, 6)
    log_txt = font.render(f"Log: {game_message}", True, WHITE)
    screen.blit(log_txt, (log_rect.x + 15, log_rect.y + 14))

    # Turn Indicator Banner
    turn_str = f"TURN: {turn.upper()}"
    turn_col = GREEN if turn == "player" else RED
    turn_surf = font_bold.render(turn_str, True, turn_col)
    screen.blit(turn_surf, (50 + offset[0], 445 + offset[1]))

    # Render Particles & Floating Numbers
    for p in particles: p.draw(screen, offset)
    for ft in floating_texts: ft.draw(screen, offset)

    # --- Group 08 Documentation Modal Overlay (Member 5) ---
    if show_docs_modal:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(120, 60, 760, 580)
        pygame.draw.rect(screen, (35, 40, 65), modal_rect, 0, 12)
        pygame.draw.rect(screen, GOLD, modal_rect, 3, 12)

        m_title = title_font.render("PSB Academy - Group 08 Documentation", True, GOLD)
        screen.blit(m_title, (modal_rect.x + 30, modal_rect.y + 20))

        docs_lines = [
            "Module: ITGP2008 Introduction to Programming (DICT/DNDFC)",
            "Project: PSB Roman Battle Game - Mythic Clash (Group 08 - Ultimate Edition)",
            "",
            "Team Members & Task Distribution (5 Members):",
            "  • Member 1 (Thant Zin Min Htike): OOP Architecture, Pygame Engine & Window Setup",
            "  • Member 2: Unit Classes (Warrior/Tanker) & Attribute Initial Values (HP, ATK, DEF)",
            "  • Member 3: Dynamic Skills, Cooldowns, Damage Formula & EXP / Level-up Rules",
            "  • Member 4: Smart AI Turn Logic & Event Log recording to 'game_event_log.txt'",
            "  • Member 5: Canvas 2D UI, Particle Physics, Screen Shake & Documentation Modal",
            "",
            "Core Programming Concepts Applied:",
            "  • Object-Oriented Programming (Classes: Unit, Skill, ScreenShake, Particle)",
            "  • Collections & Data Structures (Lists for teams, dictionaries for assets)",
            "  • Conditional & Iterative Execution (Turn progression, win/loss verification)",
            "  • File Handling & Audio (Automatic event logging & procedural sound synthesis)",
            "",
            "Press 'D' or Click 'Group 08 Docs' again to close this modal."
        ]

        dy = modal_rect.y + 65
        for line in docs_lines:
            col = WHITE if not line.startswith("  •") else GRAY
            if "Team Members" in line or "Core Programming" in line or "Module:" in line:
                col = GOLD
            l_surf = font.render(line, True, col)
            screen.blit(l_surf, (modal_rect.x + 30, dy))
            dy += 24

    pygame.display.flip()
    clock.tick(60)

pygame.quit()