# -*- coding: utf-8 -*-
"""逐步骤动画：新圆弧由圆规"划"出来"""
import os, sys, math, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from render import (Canvas, W, H, OX, OY, SC, draw_sheet, draw_header,
                    draw_elements, draw_panel, draw_dim, visible, STEPS, ACC, INK)
from draw import F, FONT_SANS, mix
from elements import E, CAT, LW, DASH

COMPASS = (92, 110, 138)

def draw_compass(cv, c, r, ang, col=COMPASS):
    th = math.radians(ang)
    pencil = (c[0]+r*math.cos(th), c[1]+r*math.sin(th))
    L = min(58.0, max(26.0, r*0.92))
    half = r/2.0
    if half > L*0.94: half = L*0.94
    h = math.sqrt(max(L*L-half*half, 1.0))
    mx, my = (c[0]+pencil[0])/2, (c[1]+pencil[1])/2
    ux, uy = (pencil[0]-c[0])/r, (pencil[1]-c[1])/r
    nx, ny = -uy, ux
    if ny < 0: nx, ny = -nx, -ny
    hinge = (mx+nx*h, my+ny*h)
    w = 0.75
    cv.polyline([hinge, c], col, w)
    cv.polyline([hinge, pencil], col, w)
    # 铰链
    cv.ring(hinge, 1.5, col, 0.8)
    cv.dot(hinge, 0.6, col)
    # 针尖
    a = math.degrees(math.atan2(c[1]-hinge[1], c[0]-hinge[0]))
    tip = (c[0]+1.9*math.cos(math.radians(a)), c[1]+1.9*math.sin(math.radians(a)))
    side = 0.85
    p1 = (c[0]+side*math.cos(math.radians(a+90)), c[1]+side*math.sin(math.radians(a+90)))
    p2 = (c[0]+side*math.cos(math.radians(a-90)), c[1]+side*math.sin(math.radians(a-90)))
    cv.d.polygon([cv.P(tip), cv.P(p1), cv.P(p2)], fill=col)
    # 笔尖
    cv.dot(pencil, 0.55, col)

def frame(i, arc_ids, idx, t, path, size=(W, H), ss=2):
    meta = STEPS[i-1]
    cv = Canvas(size[0], size[1], ss=ss); cv.set_mm(OX, OY, SC)
    draw_sheet(cv, grid=(i > 2))
    draw_header(cv, i, meta)
    anim = dict(step=i, ids=arc_ids, idx=idx, t=t)
    draw_elements(cv, i, anim=anim)
    draw_panel(cv, i, meta)
    # 圆规
    if 0 <= idx < len(arc_ids):
        e = [x for x in E if id(x) == arc_ids[idx]][0]
        ang = e['a0'] + (e['a1']-e['a0'])*t
        draw_compass(cv, e['c'], e['r'], ang)
    return cv.save(path)

def build(outdir, fps=14, size=(1800, 1280), ss=2):
    os.makedirs(outdir, exist_ok=True)
    ff = shutil.which('ffmpeg')
    if not ff:
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ff = None
    writer = None
    if ff:
        writer = subprocess.Popen([ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                   '-s', '%dx%d' % size, '-r', str(fps), '-i', '-',
                                   '-an', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p',
                                   '-crf', '20', os.path.join(outdir, 'hook-steps.mp4')],
                                  stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
    frames = []
    n = 0
    for i in range(1, 13):
        arcs = [x for x in E if x['step'] == i and x['kind'] == 'A' and x['cat'] != 'aux']
        ids = [id(x) for x in arcs]
        seq = []
        for _ in range(3): seq.append((-1, 0.0))
        for k in range(len(ids)):
            for s in range(14): seq.append((k, (s+1)/14.0))
            seq.append((k, 1.0))
        for _ in range(8): seq.append((len(ids)-1 if ids else -1, 1.0))
        for idx, t in seq:
            p = os.path.join(outdir, '_f.png')
            im = frame(i, ids, idx, t, p, size=size, ss=ss)
            if writer:
                writer.stdin.write(im.convert('RGB').tobytes())
            if n % 3 == 0 and len(frames) < 140:
                frames.append(im.convert('RGB').resize((size[0]//2, size[1]//2)))
            n += 1
    if writer:
        writer.stdin.close(); writer.wait()
    # GIF
    if frames:
        frames[0].save(os.path.join(outdir, 'hook-steps.gif'), save_all=True,
                       append_images=frames[1:], duration=int(1000/fps*3), loop=0,
                       optimize=True)
    print('frames', n)
