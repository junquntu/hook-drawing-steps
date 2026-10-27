# -*- coding: utf-8 -*-
"""作图元素 + 尺寸标注（按 GB 线型规范 + 步骤登记）"""
import math
from geom import *
from outline import outline_path

CAT = {
    'axis':  (198, 60, 58),      # 细点画线
    'known': (32, 106, 204),
    'mid':   (14, 140, 88),
    'conn':  (212, 126, 16),
    'aux':   (150, 162, 176),    # 细实线（作图线）
    'pt':    (206, 64, 48),
    'final': (26, 26, 28),       # 粗实线
    'dim':   (58, 68, 84),       # 细实线（尺寸）
    'ext':   (58, 68, 84),       # 尺寸界线
}
# 线宽（mm，按 5.55px/mm 换算；粗:细 = 3:1）
LW = {'axis':0.62,'known':0.95,'mid':0.95,'conn':0.95,'aux':0.55,'pt':0.8,'final':2.5,'dim':0.55,'ext':0.55}
DASH = {'axis':[12,2.5,1.2,2.5], 'aux':[3.0,2.2]}

E = []
def L(step, cat, p1, p2, **kw):   E.append(dict(step=step,cat=cat,kind='L',p1=p1,p2=p2,**kw))
def A(step, cat, c, r, a0, a1, **kw): E.append(dict(step=step,cat=cat,kind='A',c=c,r=r,a0=a0,a1=a1,**kw))
def CIRC(step, cat, c, r, **kw):  E.append(dict(step=step,cat=cat,kind='C',c=c,r=r,**kw))
def PT(step, cat, p, label=None, side=(1,1), ptype='cen', labpos=None):
    E.append(dict(step=step,cat=cat,kind='P',p=p,label=label,side=side,ptype=ptype,labpos=labpos))
def DIM(step, **kw):  E.append(dict(step=step,cat='dim',kind='DIM',**kw))

# ---------------- 外轮廓 ----------------
OUT_STEP = [4,4,4,4,4, 9, 5, 7, 10, 6, 5, 8, 4, 4, 4, 4]
OUT_CAT  = ['known']*5+['conn','known','mid','conn','mid','known','conn']+['known']*4
for seg, st, cat in zip(outline_path(), OUT_STEP, OUT_CAT):
    if seg[0]=='L': L(st,cat,seg[1],seg[2])
    else:           A(st,cat,seg[1],seg[2],seg[3],seg[4])

# 倒角 C2 下缘可见棱线（全宽水平线）—— 原图上部中间那条线
L(4,'known',(-NECK_HW, TOP_Y-CHAM),(NECK_HW, TOP_Y-CHAM))
# 肩部平面（全宽粗实线）
L(4,'known',(-SH_HW, SH_Y),(SH_HW, SH_Y))

# ---------------- 第3步 基准线（超出轮廓 5mm） ----------------
L(3,'axis',(0,-53),(0,133))            # 竖直基准
L(3,'axis',(-50,0),(63,0))             # 水平基准
L(3,'axis',(9,-52),(9,12))             # O1 基准
L(3,'axis',(-63,-15),(-40,-15))        # C1 基准（15）
L(3,'ext',(-75,0),(-50,0))             # 90/15 尺寸界线（水平基准延长）
L(3,'ext',(-78,-15),(-63,-15))         # 15 尺寸界线
PT(3,'pt',(0,0),'O',(-1,1))
PT(3,'pt',(9,0),'O1',(1,1))
DIM(3, t='dv', y1=-15, y2=0, x=-75, txt='15', constr=False)
DIM(3, t='dh', x1=0, x2=9, y=-31, txt='9', e1=(0,-31), e2=(9,-31), constr=False)

# ---------------- 第4步 钩柄/肩部 ----------------
DIM(4, t='dh', x1=-11.5, x2=11.5, y=132, txt='φ23', e1=(-11.5,126), e2=(11.5,126), constr=False)
DIM(4, t='dv', y1=90, y2=128, x=-75, txt='38', e1=(-9.5,128), e2=(-15,90), constr=False)
DIM(4, t='dv', y1=0, y2=90, x=-75, txt='90', e1=(-15,90), constr=False)
DIM(4, t='dh', x1=-15, x2=15, y=78, txt='φ30', e1=(-15,90), e2=(15,90), constr=False)
DIM(4, t='lead', p=(10.6,126.9), txtpos=(22,130), txt='C2', constr=False)
DIM(4, t='dr', c=(11.5,91.5), r=1.5, a=52, txt='R3.5', lead=22, through=False, constr=False)

# ---------------- 第5步 φ40 / R48 ----------------
CIRC(5,'aux',(0,0),R20)
CIRC(5,'aux',C48,R48)
A(5,'known',(0,0),R20, ang((0,0),T_R40i_20), ang((0,0),T_20_R60)+360.0)
A(5,'known',C48,R48, ang(C48,T_R48_R40u), ang(C48,T_R48_R23)-360.0)
DIM(5, t='dd', c=(0,0), r=20, a=45, txt='φ40', lead=17, constr=False)
DIM(5, t='dr', c=C48, r=R48, a=-40, txt='R48', lead=20, constr=False)

# ---------------- 第6步 R40(内) ----------------
A(6,'aux',(0,0),60.0, 10.0, 64.0)
PT(6,'pt',C40i,'C1',(-1,-1),labpos=(-62,-18))
A(6,'mid',C40i,R40i, ang(C40i,T_R4_R40i), ang(C40i,T_R40i_20))
DIM(6, t='dr', c=(0,0), r=60.0, a=50, txt='R60\n(40+20)', lead=11, constr=True)
DIM(6, t='dr', c=C40i, r=R40i, a=26, txt='R40', lead=10, constr=False)

# ---------------- 第7步 R23 ----------------
A(7,'aux',C48,71.0, 150.0, 212.0)
PT(7,'pt',C23,'C2',(-1,0),labpos=(-65,4))
A(7,'mid',C23,R23, 0.0, ang(C23,T_R23_R4))
DIM(7, t='dr', c=C48, r=71.0, a=172, txt='R71\n(48+23)', lead=13, constr=True)
DIM(7, t='dr', c=C23, r=R23, a=20, txt='R23', txtpos=(-54,-8), constr=False)

# ---------------- 第8步 R60 ----------------
L(8,'aux',(45.0,40.0),(45.0,72.0))
A(8,'aux',(0,0),80.0, 24.0, 68.0)
PT(8,'pt',C60,'C3',(1,1))
A(8,'conn',C60,R60, ang(C60,T_20_R60), ang(C60,T_R60_L))
DIM(8, t='dh', x1=-15, x2=45, y=97, txt='60', txtx=20, e1=(-15,66.14), e2=(45,66.14), constr=True)
DIM(8, t='dr', c=(0,0), r=80.0, a=60, txt='R80\n(60+20)', lead=11, constr=True)
DIM(8, t='dr', c=C60, r=R60, a=205, txt='R60', lead=-5, constr=False)

# ---------------- 第9步 R40(上) ----------------
L(9,'aux',(55.0,52.0),(55.0,86.0))
A(9,'aux',C48,88.0, 30.0, 80.0)
PT(9,'pt',C40u,'C4',(1,-1))
A(9,'conn',C40u,R40u, 180.0, ang(C40u,T_R48_R40u))
DIM(9, t='dh', x1=15, x2=55, y=86, txt='40', txtx=37, e1=(15,75.02), e2=(55,75.02), constr=True)
DIM(9, t='dr', c=C48, r=88.0, a=50, txt='R88\n(48+40)', lead=11, constr=True)
DIM(9, t='dr', c=C40u, r=R40u, a=212, txt='R40', txtpos=(34.5,62), constr=False)

# ---------------- 第10步 R4 ----------------
A(10,'aux',C23,R23+R4, 14.0, 62.0)
A(10,'aux',C40i,R40i-R4, 35.0, 100.0)
PT(10,'pt',CT,'C5',(0,0),labpos=(-52,9))
A(10,'conn',CT,R4, ang(CT,T_R23_R4), ang(CT,T_R4_R40i))
DIM(10, t='dr', c=C23, r=R23+R4, a=58, txt='R27\n(23+4)', txtpos=(-62,37), constr=True)
DIM(10, t='dr', c=C40i, r=R40i-R4, a=100, txt='R36\n(40-4)', txtpos=(-88,26), constr=True)
DIM(10, t='dr', c=CT, r=R4, a=105, txt='R4', lead=15, through=False, constr=False)
for tp in (T_R23_R4,T_R4_R40i,T_R48_R40u,T_R48_R23,T_R40i_20,T_20_R60,T_R60_L,
           P_BODY_R,(NECK_HW,SH_Y+F_DRAW),(SH_HW-F35+F_DRAW,SH_Y)):
    PT(10,'pt',tp,None,ptype='tan')

# ---------------- 第11步 标注尺寸（底稿） ----------------
DIM(11, t='dh', x1=-11.5, x2=11.5, y=132, txt='φ23', e1=(-11.5,126), e2=(11.5,126))
DIM(11, t='dv', y1=90, y2=128, x=-75, txt='38', e1=(-9.5,128), e2=(-15,90))
DIM(11, t='dv', y1=0, y2=90, x=-75, txt='90', e1=(-15,90))
DIM(11, t='dv', y1=-15, y2=0, x=-75, txt='15')
DIM(11, t='dh', x1=-15, x2=15, y=78, txt='φ30', e1=(-15,90), e2=(15,90))
DIM(11, t='dh', x1=0, x2=9, y=-31, txt='9', e1=(0,-31), e2=(9,-31))
DIM(11, t='dd', c=(0,0), r=20, a=45, txt='φ40', lead=17)
DIM(11, t='dr', c=C48, r=R48, a=-40, txt='R48', lead=20)
DIM(11, t='dr', c=C40i, r=R40i, a=26, txt='R40', lead=10)
DIM(11, t='dr', c=C23, r=R23, a=20, txt='R23', txtpos=(-54,-8))
DIM(11, t='dr', c=C60, r=R60, a=210, txt='R60', txtpos=(-19,45))
DIM(11, t='dr', c=C40u, r=R40u, a=212, txt='R40', txtpos=(34.5,62))
DIM(11, t='dr', c=CT, r=R4, a=105, txt='R4', lead=15, through=False)
DIM(11, t='lead', p=(10.6,126.9), txtpos=(22,130), txt='C2')
DIM(11, t='dr', c=(11.5,91.5), r=1.5, a=52, txt='R3.5', lead=22, through=False)

# ---------------- 第12步 描深 ----------------
for seg in outline_path():
    if seg[0]=='L': L(12,'final',seg[1],seg[2])
    else:           A(12,'final',seg[1],seg[2],seg[3],seg[4])
L(12,'final',(-NECK_HW, TOP_Y-CHAM),(NECK_HW, TOP_Y-CHAM))
L(12,'final',(-SH_HW, SH_Y),(SH_HW, SH_Y))
