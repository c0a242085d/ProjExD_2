import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = { # 移動量辞書
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectか爆弾Rect
    戻り値：横方向、縦方向の画面内外判定結果
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True , True #初期値 画面内
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    bg = pg.Surface((WIDTH, HEIGHT))
    bg.set_alpha(200)
    bg.fill((0, 0, 0))
    screen.blit(bg, (0, 0))
    font = pg.font.Font(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    img = pg.image.load("fig/8.png")
    img = pg.transform.rotozoom(img, 0, 0.8)
    left_rect = img.get_rect(center=(text_rect.left -80, HEIGHT//2))
    right_rect = img.get_rect(center=(text_rect.right +80, HEIGHT//2))
    screen.blit(img, left_rect)
    screen.blit(img, right_rect)
    screen.blit(text, text_rect)
    pg.display.update()
    time.sleep(5)  

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_img(sum_mv: tuple[int, int], base_img: pg.Surface) -> pg.Surface:
    flipped = pg.transform.flip(base_img, True, False)
    kk_imgs = {
        (0, 0): base_img,
        (-5, 0): base_img,
        (-5, -5): pg.transform.rotozoom(base_img, 45, 1.0),
        (0, -5): pg.transform.rotozoom(base_img, 90, 1.0),
        (-5, 5): pg.transform.rotozoom(base_img, -45, 1.0),
        (0, 5): pg.transform.rotozoom(base_img, -90, 1.0),
        (5, 0): flipped,
        (5, -5): pg.transform.rotozoom(flipped, -45, 1.0),
        (5, 5): pg.transform.rotozoom(flipped, 45, 1.0),
    }
    return kk_imgs.get(sum_mv, base_img)

import math

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    distance = math.hypot(dx, dy)
    if distance == 0:
        return (0, 0)
    if distance < 300:
        return current_xy
    scale = math.sqrt(50) / distance
    vx = dx * scale
    vy = dy * scale
    return vx, vy

    

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20,20)) #空の
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) #赤い円を描く
    bb_img.set_colorkey((0,0,0))
    bb_rct = bb_img.get_rect() #爆弾Rectを習得
    bb_rct.centery = random.randint(0, WIDTH) #
    bb_rct.centery = random.randint(0, HEIGHT) #
    vx, vy = +5, +5
    clock = pg.time.Clock()
    tmr = 0

    bb_imgs, bb_accs = init_bb_imgs()

    vx, vy = +5, +5  # 最初の速度
    tmr = 0          # 経過時間カウンタ

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
             return

        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾が衝突
            gameover(screen)
            return

        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  

        screen.blit(kk_img, kk_rct)

        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        acc = bb_accs[idx]    
        bb_imgs, bb_accs = init_bb_imgs()
        avx = vx*bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]

        kk_base_img = pg.image.load("fig/3.png") 
        kk_img = get_kk_img(tuple(sum_mv), kk_base_img) 
        screen.blit(kk_img, kk_rct)

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))




        bb_rct.move_ip(vx * acc, vy * acc)
    
        yoko, tate = check_bound(bb_rct)
        if not yoko: 
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
