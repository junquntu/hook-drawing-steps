# -*- coding: utf-8 -*-
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
from geom import *
from elements import E, CAT, LW, DASH
from outline import outline_path
from steps_text import STEPS

W, H = 1800, 1280
PANEL = (40, 120, 1250, 1180)
RPNL  = (1276, 120, 1770, 1180)
OX, OY, SC = 695, 880, 5.55

INK=(32,38,46); GREY=(108,118,130); LGREY=(168,176,186)
BG=(255,255,255); LINE=(226,232,240)
ACC=(206,92,58)
BOXES=[]

def muted(c): return mix(c, BG, 0.52)

# ------------------------------------------------------------------ 尺寸标注
def _arrow(cv, tip, ang, col, size=2.7, w=0.5):
    a = math.radians(ang)
    L, Wd = size, size*0.32
    bx, by = tip[0]-L*math.cos(a), tip[1]-L*math.sin(a)
    p1 = (bx + Wd*math.sin(a), by - Wd*math.cos(a))
    p2 = (bx - Wd*math.sin(a), by + Wd*math.cos(a))
    cv.d.polygon([cv.P(tip), cv.P(p1), cv.P(p2)], fill=col)

def _txt(cv, p, s, size, col, anchor='mm', rot=0, halo=BG):
    lines = s.split('\n')
    lh = size*1.28/cv.sc
    y0 = p[1] + (len(lines)-1)*lh/2
    for k, ln in enumerate(lines):
        pp = (p[0], y0 - k*lh)
        if rot:
            cv.text_rot(pp, ln, size, col, rot=90, halo=halo)
        else:
            if halo is not None:
                x, y = cv.P(pp)
                f = F(FONT_SANS, size*cv.SS)
                bb = f.getbbox(ln)
                wpx, hpx = (bb[2]-bb[0]), (bb[3]-bb[1])
                ax = {'mm':0.5,'lm':0.0,'rm':1.0,'mb':0.5,'mt':0.5,'la':0.0,'ra':1.0}[anchor]
                ay = {'mm':0.5,'lm':0.5,'rm':0.5,'mb':1.0,'mt':0.0,'la':0.15,'ra':0.15}[anchor]
                bx = x - wpx*ax - 3*cv.SS
                by = y - hpx*ay - 2*cv.SS
                BOXES.append((bx, by, bx+wpx+6*cv.SS, by+hpx+4*cv.SS, ln))
                cv.d.rectangle([bx, by, bx+wpx+6*cv.SS, by+hpx+4*cv.SS], fill=halo)
            cv.text(pp, ln, size, col, anchor=anchor)

def draw_dim(cv, d, col, hl=False, tsize=15.0):
    t = d['t']; lw = 0.62 if not hl else 0.85
    if t in ('dh','dv'):
        if t=='dh':
            x1,x2,y = d['x1'],d['x2'],d['y']
            for ex,ey,xx in ((d.get('e1') or (None,None))[0], (d.get('e1') or (None,None))[1], x1), \
                            ((d.get('e2') or (None,None))[0], (d.get('e2') or (None,None))[1], x2):
                if ex is None: continue
                sgn = 1 if y>ey else -1
                cv.polyline([(ex,ey),(ex,y+sgn*2.2)], col, lw)
                cv.polyline([(ex,y),(xx,y)], col, lw) if abs(ex-xx)>0.2 else None
            cv.polyline([(x1,y),(x2,y)], col, lw)
            _arrow(cv,(x1,y),180,col); _arrow(cv,(x2,y),0,col)
            tx = d.get('txtx', (x1+x2)/2)
            _txt(cv,(tx, y+1.6), d['txt'], tsize, col, 'mb')
        else:
            y1,y2,x = d['y1'],d['y2'],d['x']
            for ex,ey,yy in ((d.get('e1') or (None,None))[0],(d.get('e1') or (None,None))[1],y1), \
                            ((d.get('e2') or (None,None))[0],(d.get('e2') or (None,None))[1],y2):
                if ex is None: continue
                sgn = 1 if x>ex else -1
                cv.polyline([(ex,ey),(x+sgn*2.2,ey)], col, lw)
            cv.polyline([(x,y1),(x,y2)], col, lw)
            _arrow(cv,(x,y1),270,col); _arrow(cv,(x,y2),90,col)
            _txt(cv,(x-1.8,(y1+y2)/2), d['txt'], tsize, col, 'mm', rot=1)
    elif t=='dr':
        c,r,a = d['c'],d['r'],d['a']
        th = math.radians(a)
        u = (math.cos(th), math.sin(th))
        pa = (c[0]+r*u[0], c[1]+r*u[1])
        lead = d.get('lead', 8)
        through = d.get('through', True)
        if d.get('hide'): return
        if 'txtpos' in d:
            tp = d['txtpos']
            cv.polyline([tp, pa], col, lw)
            la = math.degrees(math.atan2(pa[1]-tp[1], pa[0]-tp[0]))
            _arrow(cv, pa, la, col)
            dx, dy = pa[0]-tp[0], pa[1]-tp[1]
            if abs(dx) > abs(dy)*0.8:
                anc = 'rm' if dx > 0 else 'lm'
            else:
                anc = 'mb' if dy > 0 else 'mt'
                tp = (tp[0], tp[1] + (0.8 if dy < 0 else -0.8))
        else:
            if through:
                cv.polyline([c, (pa[0]+u[0]*max(lead,3), pa[1]+u[1]*max(lead,3))], col, lw)
                _arrow(cv, pa, a, col)
                tp = (c[0]+(r+lead)*u[0], c[1]+(r+lead)*u[1])
            else:
                cv.polyline([(pa[0]+u[0]*abs(lead), pa[1]+u[1]*abs(lead)), pa], col, lw)
                _arrow(cv, pa, a+180, col)
                tp = (pa[0]+u[0]*(abs(lead)+1.5), pa[1]+u[1]*(abs(lead)+1.5))
            anc = 'lm' if math.cos(th)>0.2 else ('rm' if math.cos(th)<-0.2 else 'mm')
        if d['txt']:
            _txt(cv, tp, d['txt'], tsize, col, anc)
    elif t=='lead':
        p0=d['p']; tp=d['txtpos']
        cv.polyline([tp,p0], col, lw)
        la = math.degrees(math.atan2(p0[1]-tp[1], p0[0]-tp[0]))
        _arrow(cv, p0, la, col)
        dx,dy = p0[0]-tp[0], p0[1]-tp[1]
        anc = 'rm' if dx>0 else ('lm' if dx<0 else 'mm')
        _txt(cv, tp, d['txt'], tsize, col, anc)
    elif t=='dd':
        c,r,a = d['c'],d['r'],d['a']
        th=math.radians(a); u=(math.cos(th),math.sin(th))
        p1=(c[0]-r*u[0],c[1]-r*u[1]); p2=(c[0]+r*u[0],c[1]+r*u[1])
        lead=d.get('lead',12)
        e=(c[0]+(r+lead)*u[0], c[1]+(r+lead)*u[1])
        cv.polyline([p1,e], col, lw)
        _arrow(cv,p1,a+180,col); _arrow(cv,p2,a,col)
        anc = 'lm' if math.cos(th)>0.2 else 'rm'
        _txt(cv,(e[0]+u[0]*1.0,e[1]+u[1]*1.0), d['txt'], tsize, col, anc)

# ------------------------------------------------------------------ 图纸
def draw_sheet(cv, grid=True):
    cv.d.rectangle([0,0,W*cv.SS,H*cv.SS], fill=BG)
    cv.d.rectangle([0,0,W*cv.SS,96*cv.SS], fill=(247,250,253))
    cv.d.line([(0,96*cv.SS),(W*cv.SS,96*cv.SS)], fill=LINE, width=2*cv.SS)
    x0,y0,x1,y1 = PANEL
    cv.d.rectangle([x0*cv.SS,y0*cv.SS,x1*cv.SS,y1*cv.SS], fill=(253,254,255), outline=LINE, width=2*cv.SS)
    if not grid: return
    for gx in range(-120,105,10):
        px=OX+gx*SC
        if x0<px<x1: cv.d.line([(px*cv.SS,y0*cv.SS),(px*cv.SS,y1*cv.SS)], fill=(243,247,251), width=cv.SS)
    for gy in range(-50,150,10):
        py=OY-gy*SC
        if y0<py<y1: cv.d.line([(x0*cv.SS,py*cv.SS),(x1*cv.SS,py*cv.SS)], fill=(243,247,251), width=cv.SS)
    rx0,ry0,rx1,ry1 = RPNL
    cv.d.rectangle([rx0*cv.SS,ry0*cv.SS,rx1*cv.SS,ry1*cv.SS], fill=(250,251,253), outline=LINE, width=2*cv.SS)

def draw_header(cv,i,meta):
    n=len(STEPS)
    cv.text_px(46,18,'%02d'%i,42,(206,92,58),bold=True)
    cv.text_px(104,26,meta['name'],29,INK,bold=True)
    cv.text_px(46,68,'吊钩 · 尺规作图分步图解    |    1-12 抄画平面图形大作业（续）作业 2',14.5,GREY)
    cv.text_px(1752,20,'第 %d 步 / 共 %d 步'%(i,n),15,GREY,anchor='ra')
    for k in range(n):
        cx=1752-(n-1-k)*14
        fill=(206,92,58) if k+1<=i else (255,255,255)
        out=(206,92,58) if k+1<=i else (198,206,216)
        cv.d.ellipse([(cx-4)*cv.SS,(48-4)*cv.SS,(cx+4)*cv.SS,(48+4)*cv.SS],fill=fill,outline=out,width=cv.SS)
    cv.text_px(1752,64,'制图：DeepSeek XH',11.5,(150,158,170),anchor='ra')
    cv.text_px(1752,80,'来自 414',11.5,(150,158,170),anchor='ra')

def wrap(cv,s,size,maxw):
    f=F(FONT_SANS,size*cv.SS); out,line=[],''
    for ch in s:
        if ch=='\n': out.append(line); line=''; continue
        t=line+ch
        if f.getlength(t)/cv.SS>maxw and line: out.append(line); line=ch
        else: line=t
    if line: out.append(line)
    return out

def block(cv,x,y,w,lines,size=15,color=INK,lh=1.62,bullet=None):
    yy=y
    for s in lines:
        for k,ln in enumerate(wrap(cv,s,size,w-(15 if bullet else 0))):
            if bullet and k==0: cv.text_px(x,yy,bullet,size,ACC,bold=True)
            cv.text_px(x+(15 if bullet else 0),yy,ln,size,color)
            yy+=size*lh
        yy+=size*0.30
    return yy

def draw_panel(cv,i,meta):
    rx0,ry0,rx1,ry1=RPNL
    x=rx0+26; w=(rx1-rx0)-52
    cv.text_px(x,ry0+22,'本 步 操 作',14.5,ACC,bold=True)
    cv.d.line([(x*cv.SS,(ry0+44)*cv.SS),((x+40)*cv.SS,(ry0+44)*cv.SS)],fill=ACC,width=2*cv.SS)
    y=block(cv,x,ry0+60,w,meta['bullets'],14.8,INK,1.66,bullet='·')
    yb=max(y+26, ry0+232)
    cv.d.line([(x*cv.SS,yb*cv.SS),((rx1-26)*cv.SS,yb*cv.SS)],fill=LINE,width=2*cv.SS)
    cv.text_px(x,yb+16,'作 图 要 点',14.5,(32,106,204),bold=True)
    block(cv,x,yb+50,w,meta['notes'],13.9,(60,70,84),1.60)
    yl=980
    cv.d.line([(x*cv.SS,yl*cv.SS),((rx1-26)*cv.SS,yl*cv.SS)],fill=LINE,width=2*cv.SS)
    cv.text_px(x,yl+14,'图 例',13,GREY,bold=True)
    items=[('axis','基准线'),('known','已知线段'),('mid','中间线段'),('conn','连接线段'),('aux','作图辅助线')]
    for k,(c,t) in enumerate(items):
        yy=yl+44+k*24
        p1=((x-OX)/SC,(OY-yy)/SC); p2=((x+30-OX)/SC,(OY-yy)/SC)
        if c=='axis': cv.polyline([p1,p2],CAT[c],1.1,DASH['axis'])
        elif c=='aux': cv.polyline([p1,p2],CAT[c],1.0,DASH['aux'])
        else: cv.polyline([p1,p2],CAT[c],2.0)
        cv.text_px(x+40,yy-8,t,12.8,(70,80,92))
    ys=700
    cv.d.line([(x*cv.SS,ys*cv.SS),((rx1-26)*cv.SS,ys*cv.SS)],fill=LINE,width=2*cv.SS)
    cv.text_px(x,ys+12,'进 度',13,GREY,bold=True)
    for k,st in enumerate(STEPS):
        yy=ys+38+k*18.4
        cur=(k+1==i); done=(k+1<i)
        if cur:
            cv.d.rounded_rectangle([(x-8)*cv.SS,(yy-2)*cv.SS,(rx1-18)*cv.SS,(yy+15)*cv.SS],radius=4*cv.SS,fill=(253,240,232))
        col=ACC if cur else ((112,124,138) if done else (178,186,196))
        cv.text_px(x,yy,'%02d'%(k+1),11,col,bold=cur)
        cv.text_px(x+28,yy,st['short'],12.1,(46,54,64) if (cur or done) else (152,160,170),bold=cur)

# ------------------------------------------------------------------ 元素
def visible(e, cur):
    st = e['step']
    if st > cur: return False
    if cur >= 12:
        if e['kind']=='DIM': return st == 11
        if e['kind']=='P': return False
        if e['cat'] in ('known','mid','conn','aux'): return False
        return True
    if cur == 11:
        if e['kind']=='DIM': return st == 11
        if e['kind']=='P': return False
        return True
    return True

def draw_elements(cv, cur, anim=None):
    for e in E:
        if not visible(e, cur): continue
        new = (e['step'] == cur)
        cat = e['cat']
        if cat=='final' and cur>=12: new = True
        if cat in ('dim','ext'):
            if cat=='ext':
                cv.polyline([e['p1'],e['p2']], muted((88,98,112)) if not new else ACC, LW['ext'])
                continue
            if cur>=12:
                draw_dim(cv, e, (52,62,76), hl=False)
            else:
                draw_dim(cv, e, ACC if new else muted((88,98,112)), hl=new)
            continue
        col = CAT[cat] if new else muted(CAT[cat])
        if cur>=11 and cat=='axis': col = CAT['axis']
        lw = LW[cat] * (1.25 if new else 1.0)
        if cat=='aux' and not new: lw = 0.7
        k=e['kind']
        glow = new and cat not in ('axis','final')
        if k=='L':
            if glow: cv.polyline([e['p1'],e['p2']], mix(CAT[cat],BG,0.80), lw*5.2)
            cv.polyline([e['p1'],e['p2']], col, lw, DASH.get(cat))
        elif k=='A':
            a0, a1 = e['a0'], e['a1']
            if anim and anim['step']==cur and id(e) in anim['ids']:
                k = anim['ids'].index(id(e))
                if k > anim['idx']: continue
                if k == anim['idx']: a1 = a0 + (a1-a0)*anim['t']
            if glow: cv.arc(e['c'],e['r'],a0,a1, mix(CAT[cat],BG,0.80), lw*5.2)
            cv.arc(e['c'],e['r'],a0,a1, col, lw, DASH.get(cat))
        elif k=='C':
            if glow: cv.arc(e['c'],e['r'],0,360, mix(CAT[cat],BG,0.80), lw*5.2)
            cv.arc(e['c'],e['r'],0,360, col, lw, DASH.get(cat))
        elif k=='P':
            if e['ptype']=='tan':
                cv.ring(e['p'], 1.5, ACC if (new or cur>=11) else muted(ACC), 1.0)
                if new or cur>=11:
                    cv.dot(e['p'],0.55,ACC)
            else:
                p=e['p']
                cv.polyline([(p[0]-2.6,p[1]),(p[0]+2.6,p[1])], col, 0.9)
                cv.polyline([(p[0],p[1]-2.6),(p[0],p[1]+2.6)], col, 0.9)
                if e['label']:
                    cv.dot(p,0.5,col)
                    s=e['side']
                    if e.get('labpos'):
                        lp = e['labpos']
                        cv.polyline([p,lp],col,0.55,[2.4,1.8])
                        anc = 'rm' if lp[0]<p[0] else 'lm'
                        xx,yy = cv.P(lp)
                        fnt=F(FONT_SANS,13.5*cv.SS); bb=fnt.getbbox(e['label'])
                        wpx=bb[2]-bb[0]; hpx=bb[3]-bb[1]
                        bx = xx-wpx if anc=='rm' else xx
                        BOXES.append((bx-2*cv.SS, yy-hpx/2-2*cv.SS, bx+wpx+2*cv.SS, yy+hpx/2+2*cv.SS, e['label']))
                        cv.text(lp, e['label'], 13.5, col, anchor=anc)
                    else:
                        lp=(p[0]+2.2*s[0], p[1]+1.4*s[1])
                        anc='lm' if s[0]>0 else 'rm'
                        xx,yy = cv.P(lp)
                        fnt=F(FONT_SANS,13.5*cv.SS); bb=fnt.getbbox(e['label'])
                        wpx=bb[2]-bb[0]; hpx=bb[3]-bb[1]
                        bx = xx if anc=='lm' else xx-wpx
                        BOXES.append((bx-2*cv.SS, yy-hpx/2-2*cv.SS, bx+wpx+2*cv.SS, yy+hpx/2+2*cv.SS, e['label']))
                        cv.text(lp, e['label'], 13.5, col, anchor=anc)

def draw_callouts(cv, meta):
    for txt,target,pos,align in meta.get('callouts',[]):
        cv.polyline([target,pos],(158,128,116),0.5,[2.6,2.0])
        cv.dot(target,0.75,ACC)
        size=12.8
        lines=wrap(cv,txt,size,50)
        f=F(FONT_SANS,size*cv.SS)
        wpx=max(f.getlength(l) for l in lines)/cv.SS
        bx0=pos[0] if align=='la' else pos[0]-wpx
        cv.d.rectangle([(bx0-4)*cv.SS,(pos[1]-3)*cv.SS,(bx0+wpx+4)*cv.SS,(pos[1]+len(lines)*size*1.42+2)*cv.SS],fill=BG)
        for k,ln in enumerate(lines):
            cv.text_px(bx0,pos[1]+k*size*1.42,ln,size,(158,82,62))


# ------------------------------------------------------------------ 特殊步骤
from elements import OUT_CAT
def draw_overview(cv):
    segs = list(zip(outline_path(), OUT_CAT))
    for seg, cat in segs:
        col = CAT[cat]
        if seg[0]=='L': cv.polyline([seg[1],seg[2]], col, 2.4)
        else:           cv.arc(seg[1],seg[2],seg[3],seg[4], col, 2.4)
    # 基准线
    cv.polyline([(0,-45),(0,139)], CAT['axis'], 0.95, DASH['axis'])
    cv.polyline([(-112,0),(92,0)], CAT['axis'], 0.95, DASH['axis'])
    labs = [('φ23',(0,134.5),'mm','known'),('φ30',(0,85),'mm','known'),
            ('φ40',(19.5,14.5),'lm','known'),('R48',(41,-30),'lm','known'),
            ('R60',(3,29),'lm','conn'),('R40',(20,57),'lm','conn'),
            ('R40',(-27,7.5),'rm','mid'),('R23',(-43,11),'rm','mid'),
            ('R4',(-39.5,21.5),'lm','conn'),('R3.5',(17,97),'lm','known')]
    for txt,p,anc,cat in labs:
        f = F(FONT_SANS, 13.5*cv.SS)
        wpx = f.getlength(txt)/cv.SS
        bx = p[0]-wpx if anc=='rm' else (p[0]-wpx/2 if anc=='mm' else p[0])
        cv.d.rectangle([(bx-3)*cv.SS,(p[1]-3)*cv.SS,(bx+wpx+3)*cv.SS,(p[1]+15)*cv.SS], fill=BG)
        cv.text(p, txt, 13.5, CAT[cat], anchor=anc)

def draw_layout(cv):
    """A4 图框 + 标题栏 + 布图（示意）"""
    S = 3.75; SS = cv.SS
    X0, Y0 = 88, 1040
    def P(x, y):
        return ((X0 + x*S)*SS, (Y0 - y*S)*SS)
    def ln(a, b, col=(40,46,56), w=1.0):
        cv.d.line([P(*a), P(*b)], fill=col, width=max(1, int(w*SS)))
    def box(a, b, col=(40,46,56), w=1.0, fill=None):
        pa, pb = P(*a), P(*b)
        cv.d.rectangle([min(pa[0],pb[0]),min(pa[1],pb[1]),max(pa[0],pb[0]),max(pa[1],pb[1])],
                       outline=col, width=max(1,int(w*SS)), fill=fill)
    def txt(x, y, t, size, col=(52,60,72), anchor='lm', rot=0):
        if rot:
            cv.text_rot((P(x,y)[0]/SS, P(x,y)[1]/SS), t, size, col, rot=90)
        else:
            cv.d.text(P(x,y), t, font=F(FONT_SANS, size*SS), fill=col, anchor=anchor)
    box((0,210),(297,0),(150,158,168),1.2,(255,255,255))
    box((25,205),(292,5),(36,42,52),2.0)
    tx0 = 292-180
    box((tx0,61),(292,5),(36,42,52),1.6)
    for yy in (19,33,47): ln((tx0,yy),(292,yy),(36,42,52),0.8)
    for xx in (tx0+60, tx0+120): ln((xx,5),(xx,61),(36,42,52),0.8)
    for x,y,t in [(tx0+6,54,'零件名称'),(tx0+66,54,'吊  钩'),(tx0+6,40,'比  例'),(tx0+66,40,'1:1.4'),
                  (tx0+6,26,'班  级'),(tx0+66,26,'姓  名'),(tx0+126,40,'日  期'),(tx0+126,26,'成  绩'),
                  (tx0+6,12,'学  号'),(tx0+126,12,''),(tx0+66,12,'')]:
        if t: txt(x,y,t,9.5)
    K = 0.72; BX, BY = 46, 70
    def G(p): return (BX + (p[0]+45)*K, BY + (p[1]+48)*K)
    box(G((-45,-48)), G((58,128)), (196,206,218), 0.9)
    for seg in outline_path():
        if seg[0]=='L':
            cv.d.line([P(*G(seg[1])), P(*G(seg[2]))], fill=(92,112,144), width=int(1.5*SS))
        else:
            pts=[]
            for k in range(41):
                a=math.radians(seg[3]+(seg[4]-seg[3])*k/40)
                pts.append(P(*G((seg[1][0]+seg[2]*math.cos(a), seg[1][1]+seg[2]*math.sin(a)))))
            cv.d.line(pts, fill=(92,112,144), width=int(1.5*SS), joint='curve')
    cv.d.line([P(*G((0,-42))), P(*G((0,133)))], fill=(206,120,110), width=int(0.9*SS))
    cv.d.line([P(*G((0,-42))), P(*G((0,133)))], fill=(206,120,110), width=int(0.9*SS))
    ln(G((-45,-48)), G((-45,-58)), (150,160,175), 0.8)
    ln(G((58,-48)),  G((58,-58)),  (150,160,175), 0.8)
    ln(G((-45,-54)), G((58,-54)),  (150,160,175), 0.8)
    txt(*G((6,-56)), '103', 10.5, (140,150,166), 'mm')
    ln(G((-52,-48)), G((-58,-48)), (150,160,175), 0.8)
    ln(G((-52,128)), G((-58,128)), (150,160,175), 0.8)
    ln(G((-55,-48)), G((-55,128)), (150,160,175), 0.8)
    txt(*G((-63,40)), '176', 10.5, (140,150,166), 'mm')
    txt(150,196,'A4 297×210   比例自定（例 1:1.4）',11,(150,158,170),'lm')

def report_overlaps():
    bad=[]
    for i in range(len(BOXES)):
        for j in range(i+1,len(BOXES)):
            a,b=BOXES[i],BOXES[j]
            if a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]:
                bad.append((a[4],b[4]))
    return bad

def render_step(i, path):
    BOXES.clear()
    meta = STEPS[i-1]
    cv = Canvas(W,H,ss=3); cv.set_mm(OX,OY,SC)
    draw_sheet(cv, grid=(i>2))
    draw_header(cv,i,meta)
    if i==1:   draw_overview(cv)
    elif i==2: draw_layout(cv)
    else:      draw_elements(cv,i)
    draw_callouts(cv,meta)
    draw_panel(cv,i,meta)
    cv.save(path)
    return path
