# -*- coding: utf-8 -*-
import math
from geom import *

def outline_path():
    """返回闭合外轮廓的段序列：('L',p1,p2) 或 ('A',c,r,a0,a1)"""
    S = []
    A = S.append
    A(('L', P_TOP_L, P_TOP_R))
    A(('L', P_TOP_R, P_CH_R))
    A(('L', P_CH_R, P_NF_R))
    A(('A', C_F_R, F_DRAW, 180.0, 270.0))
    A(('L', P_SH_R, P_BODY_R))
    a1 = ang(C40u, T_R48_R40u)          # 238.5
    A(('A', C40u, R40u, 180.0, a1))
    a2 = ang(C48, T_R48_R23)            # 180
    A(('A', C48, R48, ang(C48, T_R48_R40u), a2 - 360.0))
    a3 = ang(C23, T_R23_R4)
    A(('A', C23, R23, 0.0, a3))
    a4 = ang(CT, T_R4_R40i)
    A(('A', CT, R4, ang(CT, T_R23_R4), a4))
    a5 = ang(C40i, T_R40i_20)
    A(('A', C40i, R40i, a4, a5))
    a6 = ang((0,0), T_20_R60)
    A(('A', (0,0), R20, ang((0,0), T_R40i_20), a6 + 360.0))
    a7 = ang(C60, T_R60_L)
    A(('A', C60, R60, ang(C60, T_20_R60), a7))
    A(('L', T_R60_L, P_SH_L))
    A(('A', C_F_L, F_DRAW, 270.0, 360.0))
    A(('L', P_NF_L, P_CH_L))
    A(('L', P_CH_L, P_TOP_L))
    return S

def draw_outline(cv, color, w, dash=None, glow=None):
    if glow:
        for seg in outline_path():
            if seg[0]=='L': cv.polyline([seg[1],seg[2]], glow, w*5.0)
            else: cv.arc(seg[1],seg[2],seg[3],seg[4], glow, w*5.0)
    for seg in outline_path():
        if seg[0]=='L': cv.polyline([seg[1],seg[2]], color, w, dash)
        else: cv.arc(seg[1],seg[2],seg[3],seg[4], color, w, dash)
