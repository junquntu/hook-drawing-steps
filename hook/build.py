# -*- coding: utf-8 -*-
"""一键生成：12 张分步图 + 总览 + 动画"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from draw import Canvas
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs')
os.makedirs(OUT, exist_ok=True)

def main(do_anim=True):
    files = []
    for i in range(1, 11):
        p = os.path.join(OUT, 'step%02d.png' % i)
        render.render_step(i, p)
        bad = render.report_overlaps()
        if bad:
            print('  [warn] step %d 文字重叠: %s' % (i, bad))
        files.append(p)
        print('rendered', p)

    # 总览
    cols, rows = 2, 5
    tw, th, gap = 740, 526, 24
    Wc = cols*tw + (cols+1)*gap
    Hc = rows*th + (rows+1)*gap + 92
    cv = Canvas(Wc, Hc, ss=2, bg=(255,255,255))
    cv.d.rectangle([0, 0, Wc*2, 92*2], fill=(247, 250, 253))
    cv.text_px(36, 20, '吊钩 · 尺规作图 10 步总览', 28, (32, 38, 46), bold=True)
    cv.text_px(36, 60, '1-12 抄画平面图形大作业（续）作业2    |    已知线段 → 中间线段 → 连接线段    |    制图：DeepSeek XH / 来自 414', 13, (120, 128, 140))
    for k, p in enumerate(files):
        r, c = divmod(k, cols)
        x = gap + c*(tw+gap); y = 92 + gap + r*(th+gap)
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        cv.img.paste(im, (int(x*cv.SS), int(y*cv.SS)))
        cv.d.rectangle([x*cv.SS, y*cv.SS, (x+tw)*cv.SS, (y+th)*cv.SS],
                       outline=(214, 222, 232), width=2*cv.SS)
    cv.save(os.path.join(OUT, '总览-12步.png'))
    print('contact sheet ok')

    if do_anim:
        import anim
        anim.build(OUT)
        print('animation ok')

if __name__ == '__main__':
    main(do_anim=('--no-anim' not in sys.argv))
