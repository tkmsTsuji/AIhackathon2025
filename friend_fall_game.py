#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 15:20:48 2025

@author: tsuji
"""

import os
import random
import pygame
import pymunk

# --- 初期化 ---
pygame.init()
screen = pygame.display.set_mode((400, 600))
clock = pygame.time.Clock()

space = pymunk.Space()
space.gravity = (0, 300)

# --- 床 ---
floor = pymunk.Segment(space.static_body, (50, 580), (350, 580), 10)
floor.friction = 1.0
space.add(floor)

# --- プレイヤー画像とプロパティ読み込み ---
image_folder = os.path.join(os.getcwd(), "images", "fontsize_64")
players = []
for filename in sorted(os.listdir(image_folder)):
    if filename.endswith(".png"):
        img = pygame.image.load(os.path.join(image_folder, filename)).convert_alpha()
        if "red" in filename:
            players.append({"name": "Red", "image": img, "mass": 2, "color": (255, 0, 0)})
        elif "blue" in filename:
            players.append({"name": "Blue", "image": img, "mass": 1, "color": (0, 0, 255)})

turn = 0  # 0:Red, 1:Blue
counters = [0, 0]  # プレイヤーごとの積み数

# --- ブロッククラス ---
class FriendBlock:
    def __init__(self, x, player):
        self.original_image = player["image"]

        # ランダムにスケーリング倍率を選択（5種類）
        self.scale_factor = random.choice([0.5, 0.75, 1.0, 1.25, 1.5])

        # スケーリング処理
        orig_w = self.original_image.get_width()
        orig_h = self.original_image.get_height()
        self.width = int(orig_w * self.scale_factor)
        self.height = int(orig_h * self.scale_factor)
        self.image = pygame.transform.smoothscale(self.original_image, (self.width, self.height))

        # pymunk 計算
        mass = player["mass"] * self.scale_factor  # 重さにも影響させるとリアル
        moment = pymunk.moment_for_box(mass, (self.width, self.height))

        self.body = pymunk.Body(mass, moment)
        self.body.position = x, 50

        self.shape = pymunk.Poly.create_box(self.body, size=(self.width, self.height))
        self.shape.friction = 0.9
        self.shape.elasticity = 0.2
        pymunk_space = pymunk.Space()
        space.add(self.body, self.shape)

        self.player_index = turn  # どっちのプレイヤーが落としたか記録

    def draw(self):
        x, y = self.body.position
        rect = self.image.get_rect(center=(x, y))
        screen.blit(self.image, rect)

    def is_out_of_bounds(self):
        _, y = self.body.position
        return y > 600

# --- ゲーム用リスト ---
friends = []
game_over = False
winner = None

# --- メインループ ---
while True:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # ゲームオーバー時の再スタート
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            friends.clear()
            counters = [0, 0]
            turn = 0
            game_over = False
            winner = None

            # --- spaceを新しく作り直す ---
            space = pymunk.Space()
            space.gravity = (0, 300)

            # 床を再登録
            floor = pymunk.Segment(space.static_body, (50, 580), (350, 580), 10)
            floor.friction = 1.0
            space.add(floor)

        # 通常プレイ時のクリック
        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            x = pygame.mouse.get_pos()[0]
            player = players[turn]
            block = FriendBlock(x, player)
            friends.append(block)
            counters[turn] += 1
            turn = (turn + 1) % 2

    if not game_over:
        space.step(1 / 60.0)

        # 崩れチェック
        for block in friends:
            if block.is_out_of_bounds():
                game_over = True
                winner = 1 - block.player_index  # 相手の勝ち
                break

    # --- 描画 ---
    for block in friends:
        block.draw()

    # 床
    pygame.draw.line(screen, (0, 0, 0), (50, 580), (350, 580), 3)

    # ターン表示
    font = pygame.font.SysFont(None, 28)
    if not game_over:
        turn_text = font.render(f"Turn: {players[turn]['name']}", True, (0, 0, 0))
        screen.blit(turn_text, (10, 10))

    # スコア表示
    for i, player in enumerate(players):
        count_text = font.render(f"{player['name']} Count: {counters[i]}", True, player["color"])
        screen.blit(count_text, (10, 40 + i * 30))

    # ゲームオーバー表示
    if game_over:
        winner_text = font.render(f"{players[winner]['name']} wins!", True, (0, 128, 0))
        screen.blit(winner_text, (100, 250))
        restart_text = font.render("Press R to restart", True, (0, 0, 0))
        screen.blit(restart_text, (100, 280))

    pygame.display.flip()
    clock.tick(60)