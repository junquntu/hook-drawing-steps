# -*- coding: utf-8 -*-
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_CAND = [
    _os.environ.get('FONT_CJK', ''),
    _os.path.join(_HERE, '..', 'assets', 'NotoSansCJKsc-Regular.otf'),
    '/workspace/videocreation/mienai/assets/fonts/NotoSansCJKsc-Regular.otf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf',
]
FONT_SANS = next((p for p in _CAND if p and _os.path.exists(p)), _CAND[1])
FONT_SERIF = FONT_SANS
_fcache = {}
def F(path, size):
    k = (path, int(size))
    if k not in _fcache:
        _fcache[k] = ImageFont.truetype(path, int(size))
    return _fcache[k]

def mix(c, bg, t):
    return tuple(int(c[i]*(1-t) + bg[i]*t) for i in range(3))

class Canvas:
    def __init__(self, w, h, ss=3, bg=(255,255,255)):
        self.W, self.H, self.SS, self.bg = w, h, ss, bg
        self.img = Image.new('RGB', (w*ss, h*ss), bg)
        self.d = ImageDraw.Draw(self.img)
        self.ox, self.oy, self.sc = 0.0, 0.0, 1.0
    # ---- 坐标 ----
    def set_mm(self, ox, oy, sc):
        self.ox, self.oy, self.sc = ox, oy, sc
    def P(self, p):
        return ((self.ox + p[0]*self.sc)*self.SS, (self.oy - p[1]*self.sc)*self.SS)
    def Ppx(self, x, y):
        return (x*self.SS, y*self.SS)
    # ---- 基础图元 ----
    def _seg(self, a, b, color, w):
        self.d.line([a, b], fill=color, width=max(1, int(round(w*self.SS))))
    def polyline(self, pts, color, w=1.0, dash=None, cap=True):
        if len(pts) < 2: return
        P = [self.P(p) if cap else p for p in pts]
        if dash is None:
            for i in range(len(P)-1):
                self._seg(P[i], P[i+1], color, w)
            return
        pat = [x*self.SS for x in dash]
        # 按图案走线
        idx, rem, on = 0, pat[0], True
        for i in range(len(P)-1):
            a, b = P[i], P[i+1]
            L = math.hypot(b[0]-a[0], b[1]-a[1])
            if L == 0: continue
            t = 0.0
            while t < L:
                step = min(rem, L-t)
                if on:
                    p0 = (a[0]+(b[0]-a[0])*t/L, a[1]+(b[1]-a[1])*t/L)
                    p1 = (a[0]+(b[0]-a[0])*(t+step)/L, a[1]+(b[1]-a[1])*(t+step)/L)
                    self._seg(p0, p1, color, w)
                t += step; rem -= step
                if rem <= 1e-6:
                    idx = (idx+1) % len(pat); rem = pat[idx]; on = not on
    def arc(self, c, r, a0, a1, color, w=1.0, dash=None, seg=180):
        """角度制，逆时针为正，从 a0 到 a1（按增量符号决定方向）"""
        n = max(8, int(abs(a1-a0)/360.0*seg)+2)
        pts = []
        for i in range(n+1):
            a = math.radians(a0 + (a1-a0)*i/n)
            pts.append((c[0]+r*math.cos(a), c[1]+r*math.sin(a)))
        self.polyline(pts, color, w, dash)
    def arc_pt(self, c, r, a):
        a = math.radians(a)
        return (c[0]+r*math.cos(a), c[1]+r*math.sin(a))
    def dot(self, p, r, color):
        x, y = self.P(p)
        r *= self.SS
        self.d.ellipse([x-r, y-r, x+r, y+r], fill=color)
    def ring(self, p, r, color, w=1.0):
        x, y = self.P(p); r *= self.SS
        self.d.ellipse([x-r, y-r, x+r, y+r], outline=color, width=max(1,int(w*self.SS)))
    def cross(self, p, r, color, w=0.9):
        x, y = self.P(p); r *= self.SS
        self.d.line([(x-r,y),(x+r,y)], fill=color, width=max(1,int(w*self.SS)))
        self.d.line([(x,y-r),(x,y+r)], fill=color, width=max(1,int(w*self.SS)))
    def arrow(self, tip, ang_deg, size=2.6, color=(0,0,0), w=0.6):
        a = math.radians(ang_deg)
        L, Wd = size, size*0.34
        bx, by = tip[0]-L*math.cos(a), tip[1]-L*math.sin(a)
        p1 = (bx + Wd*math.sin(a), by - Wd*math.cos(a))
        p2 = (bx - Wd*math.sin(a), by + Wd*math.cos(a))
        pts = [self.P(tip), self.P(p1), self.P(p2)]
        self.d.polygon(pts, fill=color)
    def text(self, p, s, size, color=(0,0,0), anchor='la', font=FONT_SANS, bold=False, rot=0):
        x, y = self.P(p)
        f = F(font, size*self.SS)
        if rot:
            # 仅支持 0/90
            tmp = Image.new('RGBA', (int(len(s)*size*self.SS*1.6)+40, int(size*self.SS*2)), (0,0,0,0))
            td = ImageDraw.Draw(tmp)
            td.text((0,0), s, font=f, fill=color+(255,))
            tmp = tmp.rotate(rot, expand=True)
            self.img.paste(tmp, (int(x-tmp.width/2), int(y-tmp.height/2)), tmp)
            return
        if bold:
            for dx, dy in ((0,0),(0.5,0),(0,0.5),(0.5,0.5)):
                self.d.text((x+dx*self.SS, y+dy*self.SS), s, font=f, fill=color, anchor=anchor)
        else:
            self.d.text((x, y), s, font=f, fill=color, anchor=anchor)
    def text_px(self, x, y, s, size, color=(0,0,0), anchor='la', font=FONT_SANS, bold=False):
        f = F(font, size*self.SS)
        if bold:
            for dx, dy in ((0,0),(0.5,0),(0,0.5),(0.5,0.5)):
                self.d.text(((x+dx)*self.SS, (y+dy)*self.SS), s, font=f, fill=color, anchor=anchor)
        else:
            self.d.text((x*self.SS, y*self.SS), s, font=f, fill=color, anchor=anchor)
    def rect(self, x0, y0, x1, y1, color, w=1.0, fill=None, radius=0):
        box = [x0*self.SS, y0*self.SS, x1*self.SS, y1*self.SS]
        if fill is not None:
            self.d.rounded_rectangle(box, radius=radius*self.SS, fill=fill,
                                     outline=color, width=max(1,int(w*self.SS)))
        else:
            self.d.rounded_rectangle(box, radius=radius*self.SS,
                                     outline=color, width=max(1,int(w*self.SS)))
    def save(self, path):
        out = self.img.resize((self.W, self.H), Image.LANCZOS)
        out.save(path)
        return out

def _text_rot(self, p, s, size, color, rot=90, halo=None):
    f = F(FONT_SANS, size*self.SS)
    bb = f.getbbox(s)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    mask = Image.new('L', (int(tw)+16, int(th)+16), 0)
    md = ImageDraw.Draw(mask)
    md.text((8-bb[0], 8-bb[1]), s, font=f, fill=255)
    mask = mask.rotate(rot, expand=True)
    x, y = self.P(p)
    if halo is not None:
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2),(-1.4,-1.4),(1.4,1.4),(-1.4,1.4),(1.4,-1.4)):
            self.img.paste(halo, (int(x-mask.width/2+dx*self.SS), int(y-mask.height/2+dy*self.SS)), mask)
    layer = Image.new('RGB', mask.size, color)
    self.img.paste(layer, (int(x-mask.width/2), int(y-mask.height/2)), mask)
Canvas.text_rot = _text_rot
