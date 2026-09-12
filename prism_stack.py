#!/usr/bin/env python3
"""PRISM STACK — neon tower-lite arcade. Python 3 + pygame. ElbowOS."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
if RECORD:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

W, H, FPS = 1080, 1920, 30
TITLE = "PRISM STACK"
HANDLE = "x.com/ElbowOS"
OUT = os.environ.get(
    "ELBOWOS_MP4",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "PRISM_STACK_ElbowOS.mp4"),
)
BG = (4, 18, 28)
TEAL = (20, 240, 210)
CORAL = (255, 92, 72)
LIME = (190, 255, 60)
SUN = (255, 210, 70)
PINK = (255, 80, 170)
ICE = (180, 230, 255)
WHITE = (244, 250, 255)
NAVY = (8, 40, 56)


def clamp(v, a, b):
    return a if v < a else b if v > b else v


class Spark:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "r")

    def __init__(self, x, y, col):
        a = random.uniform(-3.4, 0.2)
        sp = random.uniform(80, 420)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * sp, math.sin(a) * sp
        self.life = random.uniform(0.25, 0.7)
        self.col = col
        self.r = random.randint(2, 7)

    def tick(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 520 * dt
        self.life -= dt
        return self.life > 0

    def draw(self, s):
        if self.life > 0:
            pygame.draw.circle(s, self.col, (int(self.x), int(self.y)), max(1, self.r))


class Slab:
    def __init__(self, x, y, w, h, col):
        self.x, self.y, self.w, self.h, self.col = x, y, w, h, col

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.t = 0.0
        self.score = 0
        self.combo = 0
        self.floors = 0
        self.cam = 0.0
        self.parts = []
        self.stars = [
            (random.randrange(W), random.randrange(H), random.randint(1, 3),
             random.choice((ICE, TEAL, PINK, SUN)))
            for _ in range(70)
        ]
        base_w = 520
        self.stack = [Slab((W - base_w) / 2, H - 220, base_w, 72, TEAL)]
        self.dir = 1
        self.speed = 420
        self.falling = None
        self.hold = 0.18
        self.flash = 0.0
        self.spawn_mover()

    def spawn_mover(self):
        top = self.stack[-1]
        w = top.w
        col = (CORAL, LIME, SUN, PINK, TEAL, ICE)[self.floors % 6]
        self.falling = Slab(-w if self.dir > 0 else W, top.y - 86, w, 70, col)
        self.speed = min(860, 380 + self.floors * 28)
        self.hold = 0.12

    def boom(self, x, y, col, n=16):
        for _ in range(n):
            self.parts.append(Spark(x, y, col))

    def drop(self):
        if self.falling is None or self.hold > 0:
            return
        top = self.stack[-1]
        left = max(self.falling.x, top.x)
        right = min(self.falling.x + self.falling.w, top.x + top.w)
        overlap = right - left
        if overlap < 28:
            self.boom(self.falling.x + self.falling.w / 2, self.falling.y + 20, CORAL, 28)
            self.combo = 0
            self.falling = None
            self.hold = 0.35
            self.dir *= -1
            return
        perfect = abs(self.falling.x - top.x) < 10
        col = SUN if perfect else self.falling.col
        slab = Slab(left, top.y - 74, overlap, 70, col)
        self.stack.append(slab)
        self.floors += 1
        self.combo = self.combo + 1 if perfect or overlap > top.w * 0.82 else max(0, self.combo - 1)
        gain = int(overlap / 4) + (80 if perfect else 20) + self.combo * 6
        self.score += gain
        self.flash = 0.22 if perfect else 0.08
        self.boom(left, slab.y + 10, col, 10)
        self.boom(right, slab.y + 10, col, 10)
        if perfect:
            self.boom(slab.x + slab.w / 2, slab.y, SUN, 22)
        self.dir *= -1
        self.falling = None
        self.hold = 0.16
        target = H * 0.62 - slab.y
        if target > self.cam:
            self.cam = target

    def tick(self, dt, keys, auto):
        self.t += dt
        self.hold = max(0.0, self.hold - dt)
        self.flash = max(0.0, self.flash - dt)
        self.parts = [p for p in self.parts if p.tick(dt)]
        if self.falling is None:
            if self.hold <= 0:
                if len(self.stack) > 18:
                    self.stack = self.stack[-12:]
                self.spawn_mover()
        else:
            self.falling.x += self.dir * self.speed * dt
            if self.falling.x > W - 40:
                self.dir = -1
            if self.falling.x + self.falling.w < 40:
                self.dir = 1
            want = False
            if auto:
                top = self.stack[-1]
                cx = self.falling.x + self.falling.w / 2
                tx = top.x + top.w / 2
                approaching = (self.dir > 0 and cx < tx) or (self.dir < 0 and cx > tx)
                aligned = abs(cx - tx) < 18 + self.floors * 0.4
                want = aligned and not approaching and self.hold <= 0
                if self.t > 13.2 and self.hold <= 0:
                    want = True
            else:
                want = keys[pygame.K_SPACE] or keys[pygame.K_DOWN] or keys[pygame.K_k]
            if want:
                self.drop()
        want_cam = max(0.0, H * 0.62 - self.stack[-1].y)
        self.cam += (want_cam - self.cam) * min(1.0, 3.2 * dt)

    def wy(self, y):
        return y + self.cam

    def draw(self, s, font, big, tiny):
        s.fill(BG)
        pulse = 10 + int(8 * math.sin(self.t * 2.1))
        pygame.draw.circle(s, (6, 48, 58), (W // 2, int(H * 0.28)), 460 + pulse)
        pygame.draw.circle(s, (4, 32, 44), (W // 2, int(H * 0.28)), 240 + pulse // 2)
        for x, y, r, c in self.stars:
            yy = (y + int(self.t * (6 + r * 5))) % H
            pygame.draw.circle(s, c, (x, yy), r)
        pygame.draw.rect(s, (12, 60, 74), (60, 180, 20, H - 280))
        pygame.draw.rect(s, (12, 60, 74), (W - 80, 180, 20, H - 280))
        pygame.draw.rect(s, TEAL, (60, 180, 20, H - 280), 2)
        pygame.draw.rect(s, TEAL, (W - 80, 180, 20, H - 280), 2)
        for sl in self.stack:
            r = sl.rect()
            r.y = int(self.wy(sl.y))
            pygame.draw.rect(s, sl.col, r, border_radius=10)
            pygame.draw.rect(s, WHITE, r, 3, border_radius=10)
            inner = r.inflate(-18, -18)
            if inner.w > 8 and inner.h > 8:
                pygame.draw.rect(s, (255, 255, 255), inner, 1, border_radius=6)
        if self.falling:
            r = self.falling.rect()
            r.y = int(self.wy(self.falling.y))
            glow = pygame.Rect(r.x - 8, r.y - 8, r.w + 16, r.h + 16)
            pygame.draw.rect(s, self.falling.col, glow, 2, border_radius=14)
            pygame.draw.rect(s, self.falling.col, r, border_radius=10)
            pygame.draw.rect(s, WHITE, r, 3, border_radius=10)
            cx = r.centerx
            pygame.draw.line(s, PINK, (cx, 170), (cx, r.y), 4)
            pygame.draw.rect(s, PINK, (cx - 36, 160, 72, 22), border_radius=6)
        for p in self.parts:
            pygame.draw.circle(s, p.col, (int(p.x), int(self.wy(p.y))), max(1, p.r))
        if self.flash > 0:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 230, 80, int(90 * self.flash / 0.22)))
            s.blit(veil, (0, 0))
        bar = pygame.Surface((W, 168), pygame.SRCALPHA)
        bar.fill((4, 16, 24, 220))
        s.blit(bar, (0, 0))
        s.blit(big.render(TITLE, True, TEAL), (40, 22))
        s.blit(font.render(f"SCORE  {self.score:06d}   FLOOR {self.floors}   x{self.combo}", True, SUN), (40, 100))
        s.blit(tiny.render(HANDLE, True, CORAL), (W - 340, 36))
        s.blit(tiny.render("SPACE / K drop slab   keep the stack alive", True, ICE), (40, H - 70))
        pygame.draw.line(s, TEAL, (0, 168), (W, 168), 3)
        pygame.draw.line(s, CORAL, (0, H - 96), (W, H - 96), 2)


def record_reel(game, surf, font, big, tiny):
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "20", "-preset", "fast", "-movflags", "+faststart", OUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    frames = FPS * 15
    dt = 1.0 / FPS
    try:
        for _ in range(frames):
            game.tick(dt, None, auto=True)
            game.draw(surf, font, big, tiny)
            proc.stdin.write(pygame.image.tostring(surf, "RGB"))
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore") if proc.stderr else ""
        rc = proc.wait(timeout=60)
        if rc != 0:
            raise RuntimeError(err[-2000:])
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
        raise


def main():
    pygame.init()
    pygame.font.init()
    if RECORD:
        screen = pygame.Surface((W, H))
    else:
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(f"{TITLE} — {HANDLE}")
    font = pygame.font.SysFont("DejaVu Sans Mono", 36, bold=True)
    big = pygame.font.SysFont("DejaVu Sans", 64, bold=True)
    tiny = pygame.font.SysFont("DejaVu Sans Mono", 28, bold=True)
    game = Game()
    if RECORD:
        record_reel(game, screen, font, big, tiny)
        print("WROTE", OUT)
        pygame.quit()
        return
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                game.reset()
        game.tick(dt, pygame.key.get_pressed(), auto=False)
        game.draw(screen, font, big, tiny)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
