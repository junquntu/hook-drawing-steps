# -*- coding: utf-8 -*-
"""吊钩（1-12 作业2）几何模型 —— 全部由尺寸+相切条件解出"""
import math

# ---------- 基本尺寸 ----------
NECK_HW = 11.5          # Ø23 /2
SH_HW   = 15.0          # Ø30 /2
SH_Y    = 90.0          # 肩部高度（距水平中心线）
TOP_Y   = 128.0         # 顶面（38+90）
F35     = 3.5           # 颈部圆角 R3.5（标注值）
F_DRAW  = 1.5           # 图中实际画出的圆角（与原图一致，留出肩部平面）
CHAM    = 2.0           # C2 倒角

R20  = 20.0             # Ø40 圆
C20  = (0.0, 0.0)
R48, C48 = 48.0, (9.0, 0.0)
R40u = 40.0
R40i = 40.0
R60  = 60.0
R23  = 23.0
R4   = 4.0

# ---------- 圆心（由相切条件求得） ----------
# R40(上)：与 x=15 相切、与 R48 外切  -> Cx=15+40=55, |C-C48|=48+40=88
C40u = (55.0, math.sqrt(88**2 - 46**2))            # (55, 75.02)

# R40(内)：圆心在 y=-15 线上、与 φ40 外切 -> |C|=40+20=60
C40i = (-math.sqrt(60**2 - 15**2), -15.0)          # (-58.095, -15)

# R60：与 x=-15 相切、与 φ40 外切 -> Cx=45, |C|=60+20=80
C60 = (45.0, math.sqrt(80**2 - 45**2))             # (45, 66.144)

# R23：圆心在水平中心线上、与 R48 外切 -> |C-C48|=48+23=71
C23 = (C48[0] - 71.0, 0.0)                          # (-62, 0)

# R4 钩尖：与 R23 外切(|Δ|=27)、与 R40(内) 外切(|Δ|=36)
def _circle_intersect(c1, r1, c2, r2):
    d = math.hypot(c2[0]-c1[0], c2[1]-c1[1])
    a = (r1*r1 - r2*r2 + d*d) / (2*d)
    h = math.sqrt(max(r1*r1 - a*a, 0.0))
    mx = c1[0] + a*(c2[0]-c1[0])/d
    my = c1[1] + a*(c2[1]-c1[1])/d
    ux, uy = (c2[0]-c1[0])/d, (c2[1]-c1[1])/d
    return [(mx + h*(-uy), my + h*ux), (mx - h*(-uy), my - h*ux)]

_sol = _circle_intersect(C23, R23 + R4, C40i, R40i - R4)
CT = max(_sol, key=lambda p: p[1])                  # 取上方解 ≈ (-40.6, 16.5)

# ---------- 切点 ----------
def lerp_tan(c1, c2, r):     # c1 为圆心，c2 为另一点，返回距 c1 为 r 的点
    d = math.hypot(c2[0]-c1[0], c2[1]-c1[1])
    return (c1[0] + (c2[0]-c1[0])*r/d, c1[1] + (c2[1]-c1[1])*r/d)

T_R48_R40u = lerp_tan(C48, C40u, R48)               # (34.09, 40.92)
T_R48_R23  = lerp_tan(C48, C23,  R48)               # (-39, 0)
T_R23_R4   = lerp_tan(C23, CT,   R23)               # ≈ (-43.8, 14.1)
T_R4_R40i  = lerp_tan(C40i, CT,  R40i)              # ≈ (-38.7, 20.0)
T_R40i_20  = lerp_tan((0,0), C40i, R20)             # (-19.365, -5)
T_20_R60   = lerp_tan((0,0), C60,  R20)             # (11.25, 16.54)
T_R60_L    = (-15.0, C60[1])                        # (-15, 66.14)

# 颈部轮廓关键点
P_TOP_L   = (-NECK_HW + CHAM, TOP_Y)   # (-9.5,128)
P_TOP_R   = ( NECK_HW - CHAM, TOP_Y)   # ( 9.5,128)
P_CH_R    = ( NECK_HW, TOP_Y - CHAM)   # (11.5,126)
P_CH_L    = (-NECK_HW, TOP_Y - CHAM)
P_NF_R    = ( NECK_HW, SH_Y + F_DRAW)  # (11.5,91.5)
P_NF_L    = (-NECK_HW, SH_Y + F_DRAW)
C_F_R     = ( SH_HW - F35 + F_DRAW, SH_Y + F_DRAW)   # (13,91.5)
C_F_L     = (-SH_HW + F35 - F_DRAW, SH_Y + F_DRAW)
P_SH_R    = ( SH_HW, SH_Y)             # (15,90)
P_SH_L    = (-SH_HW, SH_Y)
P_BODY_R  = ( SH_HW, C40u[1])          # (15,75.02)  R40(上)切点
P_BODY_L  = (-SH_HW, C60[1])           # (-15,66.14) R60 切点

def ang(c, p):
    return math.degrees(math.atan2(p[1]-c[1], p[0]-c[0])) % 360.0

def sweep(a0, a1, cw):
    """返回从 a0 到 a1 的角度增量（带符号）"""
    d = (a1 - a0) % 360.0
    return -d if cw else d

if __name__ == '__main__':
    for n, v in [('C40u', C40u), ('C40i', C40i), ('C60', C60), ('C23', C23), ('CT', CT),
                 ('T1', T_R48_R40u), ('T2', T_R48_R23), ('T3', T_R23_R4), ('T4', T_R4_R40i),
                 ('T5', T_R40i_20), ('T6', T_20_R60)]:
        print('%-6s' % n, '(%.3f, %.3f)' % v)
