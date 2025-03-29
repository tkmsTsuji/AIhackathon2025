#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 13:00:34 2025

@author: tsuji
"""

from IPython.display import display, HTML

display(HTML('''
<div>
  <canvas id="gameCanvas" width="300" height="500" style="border:1px solid black;"></canvas>
  <p>Player: <span id="currentPlayer">1</span></p>
  <p>Player 1 Score: <span id="score1">0</span> / Player 2 Score: <span id="score2">0</span></p>
</div>

<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const gridSize = 60;
  const moveStep = 10;  // ← 横移動の単位を10pxに
  const blocks = [];
  let currentPlayer = 1;
  const scores = {1: 0, 2: 0};
  let scrollY = 0;

  const kanjiTypes = [
    { char: '友', score: 1, effect: 'normal' },
    { char: '朋', score: 2, effect: 'sticky' },
    { char: '親', score: 3, effect: 'stable' },
    { char: '知', score: 0.5, effect: 'fast' }
  ];

  function getRandomKanji() {
    return kanjiTypes[Math.floor(Math.random() * kanjiTypes.length)];
  }

  let block = createNewBlock();

  function createNewBlock() {
    const type = getRandomKanji();
    return {
      x: 120,
      y: 0,
      angle: 0,
      char: type.char,
      score: type.score,
      effect: type.effect,
      player: currentPlayer
    };
  }

  function drawBlock(b) {
    ctx.save();
    ctx.translate(b.x + gridSize/2, b.y + gridSize/2);
    ctx.rotate(b.angle * Math.PI / 180);
    ctx.font = gridSize + "px serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = b.player === 1 ? "blue" : "red";
    ctx.fillText(b.char, 0, 0);
    ctx.restore();
  }

  function drawAll() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(0, scrollY);

    for (const b of blocks) {
      drawBlock(b);
    }
    drawBlock(block);

    ctx.restore();
  }

  function getLandingY(x) {
    // X位置が近いブロックを検出（誤差対応）
    const sameXBlocks = blocks.filter(b => Math.abs(b.x - x) < gridSize / 2);
    if (sameXBlocks.length === 0) return canvas.height - gridSize;
    const ys = sameXBlocks.map(b => b.y);
    const minY = Math.min(...ys);
    return minY - gridSize;
  }

  function gameLoop() {
    const landingY = getLandingY(block.x);
    const speed = block.effect === 'fast' ? 5 : 2;
    block.y += speed;

    if (block.y >= landingY) {
      block.y = landingY;
      blocks.push({...block});
      scores[block.player] += block.score;
      updateScores();

      if (checkCollapse()) {
        triggerCollapse();
        return;
      }

      switchPlayer();
      block = createNewBlock();
    }

    // スクロール調整
    const minY = Math.min(...blocks.map(b => b.y), block.y);
    scrollY = Math.min(0, canvas.height - minY - 200);

    drawAll();
    requestAnimationFrame(gameLoop);
  }

  function checkCollapse() {
    const topBlocks = blocks.filter(b => b.y < 120);
    if (topBlocks.length < 2) return false;

    const avgX = topBlocks.reduce((sum, b) => sum + b.x, 0) / topBlocks.length;
    const center = canvas.width / 2;
    const height = canvas.height - Math.min(...blocks.map(b => b.y));

    return height > 180 && Math.abs(avgX - center) > 60;
  }

  function triggerCollapse() {
    let frame = 0;
    const interval = setInterval(() => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.translate(0, scrollY);

      blocks.forEach(b => {
        b.y += 10 + Math.random() * 5;
        b.x += (Math.random() < 0.5 ? -1 : 1) * 5;
        drawBlock(b);
      });

      ctx.restore();
      frame++;
      if (frame > 30) {
        clearInterval(interval);
        showCollapseMessage();
      }
    }, 50);
  }

  function showCollapseMessage() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = "24px sans-serif";
    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.fillText("友情が崩壊しました…", canvas.width / 2, canvas.height / 2);

    setTimeout(() => {
      location.reload();
    }, 2000);
  }

  function switchPlayer() {
    currentPlayer = currentPlayer === 1 ? 2 : 1;
    document.getElementById('currentPlayer').innerText = currentPlayer;
  }

  function updateScores() {
    document.getElementById('score1').innerText = scores[1];
    document.getElementById('score2').innerText = scores[2];
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft' && block.x >= moveStep) block.x -= moveStep;
    if (e.key === 'ArrowRight' && block.x + gridSize + moveStep <= canvas.width) block.x += moveStep;
    if (e.key === 'ArrowUp') block.angle = (block.angle + 90) % 360;
    if (e.key === 'ArrowDown') block.y += gridSize;
  });

  gameLoop();
</script>
'''))