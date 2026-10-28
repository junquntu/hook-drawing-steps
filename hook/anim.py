# -*- coding: utf-8 -*-
"""60fps 动画：用"半径尺寸线"旋转划出圆弧，逐步骤推进，带音效"""
import os, sys, math, subprocess, shutil, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from render import (Canvas, W, H, OX, OY, SC, draw_sheet, draw_header, draw_dim,
                    draw_elements, draw_panel, visible, STEPS, ACC, INK, BG)
from draw import F, FONT_SANS, mix
from elements import E, CAT, LW, DASH
import numpy as np
from PIL import Image, ImageDraw

SIZE = (1800, 1280)
SS = 2
FPS = 60
SWEEP_COL = (206, 92, 58)
RADIUS_COL = (168, 96, 70)

def ease(t):
    return t*t*(3-2*t)

def _arrow(cv, tip, ang, col, size=2.4):
    a = math.radians(ang)
    L, Wd = size, size*0.34
    bx, by = tip[0]-L*math.cos(a), tip[1]-L*math.sin(a)
    p1 = (bx + Wd*math.sin(a), by - Wd*math.cos(a))
    p2 = (bx - Wd*math.sin(a), by + Wd*math.cos(a))
    cv.d.polygon([cv.P(tip), cv.P(p1), cv.P(p2)], fill=col)

def draw_sweep(cv, e, t, col, lw):
    a0, a1 = e['a0'], e['a1']
    a = a0 + (a1-a0)*t
    cv.arc(e['c'], e['r'], a0, a, col, lw)
    tip = cv.arc_pt(e['c'], e['r'], a)
    # 半径尺寸线
    cv.polyline([e['c'], tip], RADIUS_COL, 0.45, [4.5,2.2])
    cv.dot(e['c'], 0.55, RADIUS_COL)
    _arrow(cv, tip, a, RADIUS_COL, 2.6)
    cv.ring(tip, 1.1, (255,255,255), 0.9)

def draw_line_sweep(cv, e, t, col, lw):
    p1, p2 = e['p1'], e['p2']
    q = (p1[0]+(p2[0]-p1[0])*t, p1[1]+(p2[1]-p1[1])*t)
    cv.polyline([p1, q], col, lw)
    cv.dot(q, 0.5, col)

def _top(e):
    if e['kind'] == 'DIM':
        return 0.0
    if e['kind'] == 'L':
        return max(e['p1'][1], e['p2'][1])
    if e['kind'] == 'C':
        return e['c'][1] + e['r']
    ys = []
    for k in range(9):
        a = math.radians(e['a0'] + (e['a1']-e['a0'])*k/8)
        ys.append(e['c'][1] + e['r']*math.sin(a))
    return max(ys)

def _len(e):
    if e['kind'] == 'DIM':
        return 8.0
    if e['kind'] == 'C':
        return 2*math.pi*e['r']
    if e['kind'] == 'L':
        return math.hypot(e['p2'][0]-e['p1'][0], e['p2'][1]-e['p1'][1])
    return abs(e['r']*math.radians(e['a1']-e['a0']))

def items_for(step):
    """该步骤要动画的元素（辅助线在前，其余自上而下）"""
    els = [e for e in E if e['step'] == step and visible(e, step) and e['kind'] in ('A','L','C','DIM')]
    if step == 9:
        return [e for e in els if e['kind'] == 'DIM']
    aux  = sorted([e for e in els if e['cat'] == 'aux'], key=_top, reverse=True)
    main = sorted([e for e in els if e['cat'] != 'aux'], key=_top, reverse=True)
    if step == 10:
        arcs = [e for e in main if e['kind'] == 'A']
        lins = [e for e in main if e['kind'] == 'L']
        return arcs + lins
    return aux + main

def make_base(i, skip_ids):
    meta = STEPS[i-1]
    cv = Canvas(SIZE[0], SIZE[1], ss=SS); cv.set_mm(OX, OY, SC)
    draw_sheet(cv, grid=(i > 1))
    draw_header(cv, i, meta)
    draw_elements(cv, i, skip=skip_ids)
    draw_panel(cv, i, meta)
    return cv

def frames_for(i, items):
    intro = int(FPS*0.15) if i == 10 else int(FPS*0.55)
    seq = [(-1, 0.0)]*intro
    for k, e in enumerate(items):
        L = _len(e)
        if e['kind'] == 'DIM':
            n = int(FPS*0.22)
        elif e['kind'] == 'C':
            n = int(max(26, min(60, L*0.5)))
        else:
            n = int(max(20, min(54, L*1.1)))
        for s in range(n):
            seq.append((k, ease((s+1)/n)))
        seq.append((k, 1.0))
        seq.append((k, 1.0))
    seq += [(len(items)-1 if items else -1, 1.0)]*int(FPS*0.9)
    return seq

def build_audio(events, total, path, sr=44100):
    n = int(total*sr)
    buf = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(7)
    for kind, t0, dur in events:
        i0 = int(t0*sr); i1 = min(n, int((t0+dur)*sr))
        if i1 <= i0: continue
        m = i1-i0
        tt = np.arange(m)/sr
        if kind == 'tick':
            env = np.exp(-tt*38)
            s = (np.sin(2*np.pi*1180*tt)*0.55 + rng.standard_normal(m)*0.35) * env
            buf[i0:i1] += s*0.16
        elif kind == 'scratch':
            noise = rng.standard_normal(m)
            lp = np.zeros(m); acc = 0.0
            for k in range(m):
                acc = 0.82*acc + 0.18*noise[k]; lp[k] = acc
            env = np.minimum(1, tt/0.05) * np.minimum(1, (dur-tt)/0.08)
            buf[i0:i1] += lp*env*0.10
        elif kind == 'ding':
            env = np.exp(-tt*5.0)
            s = (np.sin(2*np.pi*659*tt)+0.5*np.sin(2*np.pi*988*tt))*env
            buf[i0:i1] += s*0.12
    buf = np.clip(buf, -0.98, 0.98)
    pcm = (buf*32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())

def draw_item(cv, e, t):
    col = CAT['final'] if e['cat'] == 'final' else CAT[e['cat']]
    lw = LW[e['cat']] * (1.35 if e['cat'] != 'final' else 1.0)
    k = e['kind']
    if k == 'A':
        draw_sweep(cv, e, t, col, lw)
    elif k == 'L':
        draw_line_sweep(cv, e, t, col, lw)
    elif k == 'C':
        cv.arc(e['c'], e['r'], 90.0, 90.0 + 360.0*t, col, lw, DASH.get(e['cat']))
        cv.dot(cv.arc_pt(e['c'], e['r'], 90.0 + 360.0*t), 0.5, col)
    elif k == 'DIM':
        draw_dim(cv, e, mix(BG, col, min(1.0, t*1.5)), hl=False)

def build(outdir, do_gif=True):
    os.makedirs(outdir, exist_ok=True)
    ff = shutil.which('ffmpeg')
    if not ff:
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ff = None
    if not ff:
        print('no ffmpeg, skip video'); return
    tmp = os.path.join(outdir, '_video.mp4')
    vw = subprocess.Popen([ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                           '-s', '%dx%d' % SIZE, '-r', str(FPS), '-i', '-',
                           '-an', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p',
                           '-crf', '20', '-preset', 'medium', tmp],
                          stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    events, gif_frames = [], []
    clock, total = 0.0, 0
    last = None
    for i in range(1, 11):
        items = items_for(i)
        skip = set(id(e) for e in items)
        base = make_base(i, skip)
        base_img = base.img
        seq = frames_for(i, items)
        events.append(('tick', clock, 0.12))
        for idx, t in seq:
            cv = base
            cv.img = base_img.copy()
            cv.d = ImageDraw.Draw(cv.img)
            for k, e in enumerate(items):
                if k > idx: break
                draw_item(cv, e, 1.0 if k < idx else t)
            out = cv.img.resize(SIZE, Image.LANCZOS)
            last = out
            vw.stdin.write(out.convert('RGB').tobytes())
            if do_gif and total % 8 == 0:
                gif_frames.append(out.convert('RGB').resize((720, 512)))
            total += 1
            clock += 1.0/FPS
        dur_sweep = len(seq)/FPS
        events.append(('scratch', clock-dur_sweep, max(0.3, dur_sweep*0.92)))
    events.append(('ding', clock-0.2, 0.9))
    for _ in range(int(FPS*1.4)):
        vw.stdin.write(last.convert('RGB').tobytes())
        total += 1
    vw.stdin.close(); vw.wait()
    wav = os.path.join(outdir, '_audio.wav')
    build_audio(events, clock+1.4, wav)
    final = os.path.join(outdir, 'hook-steps.mp4')
    subprocess.run([ff, '-y', '-i', tmp, '-i', wav, '-c:v', 'copy', '-c:a', 'aac',
                    '-b:a', '128k', '-shortest', final],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(tmp); os.remove(wav)
    if do_gif and gif_frames:
        gif_frames[0].save(os.path.join(outdir, 'hook-steps.gif'), save_all=True,
                           append_images=gif_frames[1:], duration=133, loop=0, optimize=True)
    print('frames', total, 'dur %.1fs' % (total/FPS))
