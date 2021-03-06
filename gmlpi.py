#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GML for Raspberry-PI and ILI9340 LCD on SPI
 
import RPi.GPIO as GPIO
import spidev
import time
import sys

# 規定値
ver = "Vertion 1.00.00"
c_lcdWidth = 240
c_lcdHeight = 320
c_lcdPixel = 76800
c_lcdTrnLine = 8

# コマンドラインパラメータ用
argHead = ["-"] # コマンドオプション識別ヘッダ
argSepa = [":", "="]    # コマンドオプションのパラメータセパレータ
argParaX = ["x", "X"]   # X座標オプション
argParaY = ["y", "Y"]   # Y座標オプション
argParaRot = ["rot", "ROT"] # 画面向きオプション
argParaScale = ["scale", "SCALE"]   # 拡大率オプション
argParaFit = ["fit", "FIT"]         # 拡大率自動フィットオプション
argParaWidth = ["width", "WIDTH"]   # 幅指定
argParaHeight = ["height", "HEIGHT"]    # 高さ指定
argParaBoth = ["both", "BOTH"]          # 両方指定
argParaBmp = ["bmp", "BMP"]             # BMP画像ファイルオプション
argParaColor = ["color", "COLOR"]       # 描画色オプション
argParaLine = ["line", "LINE"]          # ラインオプション
argParaTextRot = ["textrot", "TEXTROT"] # テキスト進行向きオプション
argParaTextType = ["texttype", "TEXTTYPE"]  # テキストタイプオプション
argParaText = ["text", "TEXT"]              # テキストオプション
argParaHelp = ["help", "HELP"]              # ヘルプオプション
argParaDemo = ["demo", "DEMO"]              # デモオプション
argParaFill = ["fill", "FILL"]              # 塗りつぶしオプション
argParaInit = ["init", "INIT"]              # 初期化オプション
argParaExit = ["exit", "EXIT"]              # 解放オプション
# 動作モード
xpos = 0    # 座標
ypos = 0
scrrot = 0     # 画面向き
scrWidth = c_lcdWidth
scrHeight = c_lcdHeight
xScale = 1.0    # 拡大率
yScale = 1.0
fitMode = 0     # フィッティング
bmpFile = ""    # BMP画像ファイル
rColor = 255      # 色
gColor = 255
bColor = 255
x1 = 0          # 複数座標
y1 = 0
x2 = 0
y2 = 0
rotText = 0     # テキスト展開向き
typeText = 1    # テキストタイプ
strText = ""    # テキスト
fb = [] # 内部フレームバッファ
# 4x8フォント
fix48 = [
#20-2F Graph
0x00, 0x00, 0x00, 0x00, 0x44, 0x44, 0x44, 0x04, 
0xAA, 0x00, 0x00, 0x00, 0x00, 0xAE, 0xAE, 0xA0, 
0x4E, 0xEC, 0x6E, 0xE4, 0x08, 0xA2, 0x48, 0xA2, 
0x4A, 0x44, 0xAC, 0xAE, 0xC4, 0x00, 0x00, 0x00, 
0x24, 0x48, 0x84, 0x42, 0x84, 0x42, 0x24, 0x48, 
0x00, 0xA4, 0xE4, 0xA0, 0x00, 0x44, 0xE4, 0x40, 
0x00, 0x00, 0x00, 0x4C, 0x00, 0x00, 0xE0, 0x00, 
0x00, 0x00, 0x00, 0x44, 0x02, 0x24, 0x44, 0x88, 
#30-3F Nums
0x04, 0xAA, 0xAA, 0xA4, 0x04, 0xC4, 0x44, 0x4E, 
0x04, 0xAA, 0x24, 0x8E, 0x04, 0xA2, 0x42, 0xA4, 
0x02, 0x6A, 0xAE, 0x22, 0x0E, 0x8C, 0x22, 0xA4, 
0x04, 0xA8, 0xCA, 0xA4, 0x0E, 0xA2, 0x24, 0x44, 
0x04, 0xAA, 0x4A, 0xA4, 0x04, 0xAA, 0x62, 0xA4, 
0x00, 0x40, 0x04, 0x00, 0x00, 0x40, 0x04, 0x80, 
0x00, 0x24, 0x84, 0x20, 0x00, 0x0E, 0x0E, 0x00, 
0x00, 0x84, 0x24, 0x80, 0x04, 0xA2, 0x44, 0x04, 
#40-5F Alpha Big
0x04, 0xAE, 0xAE, 0x86, 0x04, 0xAA, 0xEA, 0xAA, 
0x0C, 0xAA, 0xCA, 0xAC, 0x04, 0xA8, 0x88, 0xA4, 
0x0C, 0xAA, 0xAA, 0xAC, 0x0E, 0x88, 0xE8, 0x8E, 
0x0E, 0x88, 0xE8, 0x88, 0x04, 0xA8, 0xEA, 0xA6, 
0x0A, 0xAA, 0xEA, 0xAA, 0x0E, 0x44, 0x44, 0x4E, 
0x0E, 0x44, 0x44, 0x48, 0x0A, 0xC8, 0xCA, 0xAA, 
0x08, 0x88, 0x88, 0x8E, 0x0A, 0xEA, 0xAA, 0xAA, 
0x0C, 0xAA, 0xAA, 0xAA, 0x04, 0xAA, 0xAA, 0xA4, 
0x0C, 0xAA, 0xC8, 0x88, 0x04, 0xAA, 0xAE, 0xA6, 
0x0C, 0xAA, 0xCA, 0xAA, 0x04, 0xA8, 0x42, 0xA4, 
0x0E, 0x44, 0x44, 0x44, 0x0A, 0xAA, 0xAA, 0xA4, 
0x0A, 0xAA, 0xAA, 0x44, 0x0A, 0xAE, 0xEE, 0xEA, 
0x0A, 0xAA, 0x4A, 0xAA, 0x0A, 0xAA, 0xE4, 0x44, 
0x0E, 0x22, 0x48, 0x8E, 0x0E, 0x88, 0x88, 0x8E, 
0x0A, 0xA4, 0xEE, 0x44, 0x0E, 0x22, 0x22, 0x2E, 
0x04, 0xA0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0E, 
#60-7F Alpha Little
0x42, 0x00, 0x00, 0x00, 0x00, 0x4A, 0x6A, 0xA6, 
0x08, 0x88, 0xCA, 0xAC, 0x00, 0x00, 0x68, 0x86, 
0x02, 0x22, 0x6A, 0xA6, 0x00, 0x04, 0xAE, 0x86, 
0x02, 0x44, 0xE4, 0x44, 0x00, 0x06, 0xA6, 0xA4, 
0x08, 0x88, 0xCA, 0xAA, 0x00, 0x40, 0x44, 0x44, 
0x00, 0x40, 0x44, 0x48, 0x08, 0x88, 0xAC, 0xAA, 
0x0C, 0x44, 0x44, 0x46, 0x00, 0x00, 0xAE, 0xEE, 
0x00, 0x00, 0xCA, 0xAA, 0x00, 0x00, 0x4A, 0xA4, 
0x00, 0x00, 0xCA, 0xC8, 0x00, 0x00, 0x6A, 0x62, 
0x00, 0x00, 0xAC, 0x88, 0x00, 0x06, 0x84, 0x2C, 
0x00, 0x04, 0xE4, 0x46, 0x00, 0x00, 0xAA, 0xA6, 
0x00, 0x00, 0xAA, 0x44, 0x00, 0x00, 0xEE, 0xEA, 
0x00, 0x0A, 0xA4, 0xAA, 0x00, 0x0A, 0xAE, 0x2C, 
0x00, 0x0E, 0x24, 0x8E, 0x06, 0x44, 0x84, 0x46, 
0x44, 0x44, 0x44, 0x44, 0x0C, 0x44, 0x64, 0x4C, 
0x6C, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0xEE, 0xEE, 
        ]
fix1212 = [
#30-39 Nums
0x00,0x00,0xf0, 0x10,0x83,0x0c, 0x30,0xc3,0x0c, 0x30,0xc3,0x0c, 0x30,0xc1,0x08, 0x0f,0x00,0x00,
0x00,0x00,0x20, 0x06,0x01,0xe0, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x1f,0x80,0x00,
0x00,0x00,0xf0, 0x11,0x83,0x0c, 0x30,0xc0,0x18, 0x03,0x00,0x40, 0x08,0x41,0xfc, 0x3f,0x80,0x00,
0x00,0x01,0xf0, 0x31,0x83,0x0c, 0x00,0x80,0x70, 0x00,0x80,0x0c, 0x30,0xc3,0x18, 0x1f,0x00,0x00,
0x00,0x00,0x30, 0x07,0x00,0xb0, 0x0b,0x01,0x30, 0x33,0x03,0xfc, 0x03,0x00,0x30, 0x07,0x80,0x00,
0x00,0x01,0xfc, 0x1f,0x81,0x00, 0x10,0x01,0xf0, 0x01,0x80,0x0c, 0x30,0xc3,0x18, 0x1f,0x00,0x00,
0x00,0x00,0xf0, 0x18,0x81,0x0c, 0x30,0x03,0x70, 0x39,0x83,0x0c, 0x30,0xc1,0x88, 0x0f,0x00,0x00,
0x00,0x01,0xfc, 0x3f,0x82,0x08, 0x01,0x00,0x10, 0x02,0x00,0x20, 0x06,0x00,0x60, 0x06,0x00,0x00,
0x00,0x00,0xf0, 0x19,0x83,0x0c, 0x18,0x80,0xf0, 0x11,0x83,0x0c, 0x30,0xc1,0x98, 0x0f,0x00,0x00,
0x00,0x00,0xf0, 0x11,0x83,0x0c, 0x30,0xc1,0x1c, 0x0e,0xc0,0x0c, 0x30,0x81,0x18, 0x0f,0x00,0x00,
#41-5A  Alpha Big
0x00,0x00,0x40, 0x06,0x00,0x60, 0x0b,0x00,0xb0, 0x11,0x81,0xf8, 0x20,0xc2,0x0c, 0x71,0xe0,0x00,
0x00,0x07,0xf0, 0x31,0x83,0x0c, 0x31,0x83,0xf0, 0x30,0xc3,0x06, 0x30,0x63,0x0c, 0x7f,0x80,0x00,
0x00,0x00,0xf4, 0x30,0xc3,0x04, 0x60,0x46,0x00, 0x60,0x06,0x00, 0x30,0x43,0x08, 0x0f,0x00,0x00,
0x00,0x07,0xf0, 0x31,0x83,0x04, 0x30,0x63,0x06, 0x30,0x63,0x06, 0x30,0x43,0x18, 0x7f,0x00,0x00,
0x00,0x07,0xf8, 0x30,0x43,0x00, 0x31,0x03,0xf0, 0x31,0x03,0x00, 0x30,0x23,0x04, 0x7f,0xc0,0x00,
0x00,0x07,0xf8, 0x30,0x43,0x00, 0x31,0x03,0xf0, 0x31,0x03,0x00, 0x30,0x03,0x00, 0x78,0x00,0x00,
0x00,0x00,0xf4, 0x30,0xc3,0x04, 0x60,0x06,0x00, 0x61,0xe6,0x0c, 0x30,0xc3,0x1c, 0x0e,0xc0,0x00,
0x00,0x07,0x9e, 0x30,0xc3,0x0c, 0x30,0xc3,0xfc, 0x30,0xc3,0x0c, 0x30,0xc3,0x0c, 0x79,0xe0,0x00,
0x00,0x01,0xf8, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x1f,0x80,0x00,
0x00,0x00,0x7e, 0x01,0x80,0x18, 0x01,0x80,0x18, 0x01,0x83,0x18, 0x31,0x81,0x10, 0x0e,0x00,0x00,
0x00,0x07,0x9e, 0x30,0x83,0x10, 0x32,0x03,0x70, 0x3b,0x03,0x18, 0x31,0x83,0x0c, 0x79,0xe0,0x00,
0x00,0x07,0x80, 0x30,0x03,0x00, 0x30,0x03,0x00, 0x30,0x03,0x00, 0x30,0x43,0x08, 0x7f,0x80,0x00,
0x00,0x0e,0x0e, 0x60,0xc7,0x1c, 0x71,0xc5,0xac, 0x5a,0xc4,0xcc, 0x4c,0xc4,0x0c, 0xe1,0xe0,0x00,
0x00,0x07,0x0e, 0x30,0x43,0x84, 0x2c,0x42,0x64, 0x26,0x42,0x34, 0x21,0xc2,0x0c, 0x70,0xc0,0x00,
0x00,0x00,0xf0, 0x10,0x83,0x0c, 0x60,0x66,0x06, 0x60,0x66,0x06, 0x30,0xc1,0x08, 0x0f,0x00,0x00,
0x00,0x07,0xf0, 0x30,0x83,0x0c, 0x30,0xc3,0x08, 0x3f,0x03,0x00, 0x30,0x03,0x00, 0x78,0x00,0x00,
0x00,0x00,0xf0, 0x10,0x83,0x0c, 0x60,0x66,0x06, 0x60,0x66,0xe6, 0x33,0x41,0x18, 0x0f,0xe0,0x0c,
0x00,0x07,0xf0, 0x30,0x83,0x0c, 0x30,0xc3,0x08, 0x3f,0x03,0x30, 0x31,0x83,0x0c, 0x78,0xe0,0x00,
0x00,0x01,0xe8, 0x31,0x86,0x08, 0x70,0x03,0xe0, 0x0f,0x84,0x1c, 0x60,0xc7,0x0c, 0x5f,0x80,0x00,
0x00,0x07,0xfe, 0x46,0x24,0x62, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x1f,0x80,0x00,
0x00,0x07,0x8e, 0x30,0x43,0x04, 0x30,0x43,0x04, 0x30,0x43,0x04, 0x30,0x41,0x88, 0x0f,0x00,0x00,
0x00,0x07,0x8e, 0x30,0x43,0x04, 0x18,0x81,0x88, 0x18,0x80,0xd0, 0x0d,0x00,0x60, 0x06,0x00,0x00,
0x00,0x0e,0xee, 0x66,0x46,0x64, 0x66,0x46,0xb4, 0x3b,0x83,0xb8, 0x31,0x83,0x18, 0x31,0x80,0x00,
0x00,0x07,0x8e, 0x30,0x41,0x88, 0x0d,0x00,0x60, 0x06,0x00,0xb0, 0x11,0x82,0x0c, 0x71,0xe0,0x00,
0x00,0x07,0x8e, 0x30,0x41,0x88, 0x0d,0x00,0x60, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x1f,0x80,0x00,
0x00,0x03,0xfe, 0x20,0xc4,0x18, 0x03,0x00,0x60, 0x06,0x00,0xc0, 0x18,0x23,0x04, 0x7f,0xc0,0x00,
#61-7A Alpha little
0x00,0x00,0x00, 0x00,0x00,0x00, 0x1f,0x03,0x18, 0x07,0x81,0x98, 0x31,0x83,0x1a, 0x1e,0xc0,0x00,
0x00,0x03,0x80, 0x18,0x01,0x80, 0x1b,0x01,0xd8, 0x18,0xc1,0x8c, 0x18,0xc1,0xd8, 0x3b,0x00,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x0f,0x01,0x88, 0x30,0x03,0x00, 0x30,0x01,0x88, 0x0f,0x00,0x00,
0x00,0x00,0x38, 0x01,0x80,0x18, 0x0d,0x81,0xb8, 0x31,0x83,0x18, 0x31,0x81,0xb8, 0x0d,0xc0,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x0e,0x01,0x10, 0x31,0x83,0xf8, 0x30,0x01,0x08, 0x0f,0x00,0x00,
0x00,0x00,0x38, 0x04,0xc0,0xcc, 0x0c,0x03,0xf8, 0x0c,0x00,0xc0, 0x0c,0x00,0xc0, 0x3f,0x00,0x00,
0x00,0x00,0x00, 0x00,0x00,0x0c, 0x0f,0x01,0x98, 0x19,0x80,0xf0, 0x18,0x01,0xf8, 0x30,0xc1,0xf8,
0x00,0x07,0x00, 0x30,0x03,0x00, 0x37,0x03,0x98, 0x31,0x83,0x18, 0x31,0x83,0x18, 0x7b,0xc0,0x00,
0x00,0x00,0x20, 0x07,0x00,0x20, 0x00,0x01,0xe0, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x1f,0x80,0x00,
0x00,0x00,0x20, 0x07,0x00,0x20, 0x00,0x00,0xf0, 0x03,0x00,0x30, 0x03,0x03,0x30, 0x32,0x01,0xc0,
0x00,0x07,0x00, 0x30,0x03,0x00, 0x33,0xc3,0x10, 0x36,0x03,0xe0, 0x33,0x03,0x18, 0x79,0xc0,0x00,
0x00,0x01,0xe0, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x06,0x00,0x60, 0x1f,0x80,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0xed,0xc7,0x66, 0x66,0x66,0x66, 0x66,0x66,0x66, 0xee,0xe0,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x77,0x03,0x88, 0x30,0xc3,0x0c, 0x30,0xc3,0x0c, 0x79,0xe0,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x0f,0x01,0x98, 0x30,0xc3,0x0c, 0x30,0xc1,0x98, 0x0f,0x00,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x77,0x03,0x98, 0x30,0xc3,0x0c, 0x39,0x83,0x70, 0x30,0x07,0x80,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x1d,0xc3,0x38, 0x61,0x86,0x18, 0x33,0x81,0xd8, 0x01,0x80,0x3c,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x3b,0x81,0xcc, 0x18,0xc1,0x80, 0x18,0x01,0x80, 0x3c,0x00,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x1f,0x83,0x08, 0x3c,0x00,0xf0, 0x23,0x83,0x18, 0x2f,0x00,0x00,
0x00,0x00,0x00, 0x08,0x01,0x80, 0x18,0x07,0xf0, 0x18,0x01,0x80, 0x18,0x01,0x88, 0x0f,0x00,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x73,0xc3,0x18, 0x31,0x83,0x18, 0x31,0x83,0x38, 0x1c,0xc0,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x79,0xc3,0x08, 0x19,0x01,0x90, 0x0e,0x00,0xe0, 0x04,0x00,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0xf6,0xe6,0x64, 0x66,0x46,0xb4, 0x3b,0x83,0x18, 0x31,0x80,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x3d,0xc1,0x88, 0x0d,0x00,0x60, 0x0b,0x01,0x18, 0x3b,0xc0,0x00,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x3d,0xc1,0x88, 0x0c,0x80,0xd0, 0x07,0x03,0x20, 0x32,0x01,0xc0,
0x00,0x00,0x00, 0x00,0x00,0x00, 0x3f,0x82,0x30, 0x06,0x00,0xc0, 0x18,0x43,0x08, 0x3f,0x80,0x00,
        ]
trnbuf = [] # 転送用バッファ

# パラメータ判定
def ArgCheck(argraw, arglist):
    if (argraw[0] == argHead[0]):
        for ali in range(len(arglist)):
            if (argraw[1:len(arglist[ali])+1] == arglist[ali]):
                return 0
    return -1
# 文字列判定
def StrCheck(argraw, arglist):
    for ali in range(len(arglist)):
        if (argraw[0:len(arglist[ali])] == arglist[ali]):
            return 0
    return -1

class ILI9340:
    def __init__(self):
        for n in range(c_lcdPixel*4):
            fb.append(0)        
        for n in range(c_lcdPixel*2):
            trnbuf.append(0)        

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 32000000
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(24, GPIO.OUT)
        GPIO.setup(25, GPIO.OUT)
        self.reset()
        time.sleep(0.12)

        self.write((0xEF, 0x03, 0x80, 0x02))
        self.write((0xCF, 0x00 , 0XC1 , 0X30))
        self.write((0xED, 0x64 , 0x03 , 0X12 , 0X81))
        self.write((0xE8, 0x85 , 0x00 , 0x78))
        self.write((0xCB, 0x39 , 0x2C , 0x00 , 0x34 , 0x02))
        self.write((0xF7, 0x20))
        self.write((0xEA, 0x00 , 0x00))

        self.write((0xC0, 0x23))          # Power control 1
        self.write((0xC1, 0x10))          # Power control 2
        self.write((0xC5, 0x3e, 0x28))    # VCOM Control 1
        self.write((0xC7, 0x86))          # VCOM Control 2
        self.write((0x3A, 0x55))          # COLMOD: Pixel Format Set
        self.write((0xB1, 0x00, 0x18))    # Frame Rate Control
        self.write((0xB6, 0x08, 0x82, 0x27)) # Display Function Control
        self.write((0xF2, 0x00))          # Gamma Function Disable

        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x29)

    def reset(self):
        GPIO.output(25, False)
        time.sleep(0.1)
        GPIO.output(25, True)
        time.sleep(0.1)
    def write_cmd(self, cmd):
        GPIO.output(24, False)  # RS=0
        self.spi.xfer2([cmd])
    def write_data(self, data):
        GPIO.output(24, True)   # RS=1
        self.spi.xfer2([data])
    def write(self, cmd):
        if len(cmd) == 0:
            return
        GPIO.output(24, False)  # RS=0
        self.spi.xfer2([cmd[0]])
        GPIO.output(24, True)   # RS=1
        self.spi.xfer2(list(cmd[1:]))
    def write_rgb(self, r, g, b):
        self.write_data(b & 0xF8 | g >> 5)
        self.write_data(g & 0xFC << 3 | r >> 3)
    def fill(self, r, g, b):
        self.write((0x2A, 0x00, 0x00, 0x00, 0xF0))
        self.write((0x2B, 0x00, 0x00, 0x01, 0x40))
        self.write_cmd(0x2C)
        GPIO.output(24, True)   # RS=1
        hi = b & 0xF8 | g >> 5
        lo = g & 0xFC << 3 | r >> 3
        for n in range(c_lcdWidth*c_lcdTrnLine):
            trnbuf[n*2+0] = hi
            trnbuf[n*2+1] = lo
        for n in range(c_lcdHeight/c_lcdTrnLine):
            self.spi.xfer2(trnbuf[0:c_lcdWidth*c_lcdTrnLine*2])
    def fbtrn(self):
        self.write((0x2A, 0x00, 0x00, 0x00, 0xF0))
        self.write((0x2B, 0x00, 0x00, 0x01, 0x40))
        self.write_cmd(0x2C)
        GPIO.output(24, True)   # RS=1
        for n in range(c_lcdPixel):
            hi = fb[n*4+2] & 0xF8 | fb[n*4+1] >> 5
            lo = fb[n*4+1] & 0xFC << 3 | fb[n*4+0] >> 3
            trnbuf[n*2+0] = hi
            trnbuf[n*2+1] = lo
        for n in range(c_lcdHeight/c_lcdTrnLine):
            self.spi.xfer2(trnbuf[(c_lcdWidth*c_lcdTrnLine*2)*n:(c_lcdWidth*c_lcdTrnLine*2)*(n+1)])

    def pixset(self,x,y,r,g,b):
        idx=0
        if scrrot == 0:
            if x>=0 and x<c_lcdWidth and y>=0 and y<c_lcdHeight:
                idx=(c_lcdWidth*y+c_lcdWidth-1-x)*4
        elif scrrot == 1:
            if x>=0 and x<c_lcdHeight and y>=0 and y<c_lcdWidth:
                idx=(c_lcdWidth*x+y)*4
        elif scrrot == 2:
            if x>=0 and x<c_lcdWidth and y>=0 and y<c_lcdHeight:
                idx=(c_lcdWidth*(c_lcdHeight-1-y)+x)*4
        elif scrrot == 3:
            if x>=0 and x<c_lcdHeight and y>=0 and y<c_lcdWidth:
                idx=(c_lcdWidth*(c_lcdHeight-1-x)+(c_lcdWidth-1-y))*4

        fb[idx+0]=r
        fb[idx+1]=g
        fb[idx+2]=b

    def lineset(self,x,y,x2,y2,r,g,b):
        xd=x2-x
        if xd<0:
            xd=-xd
        yd=y2-y
        if yd<0:
            yd=-yd
        if xd == 0 and yd == 0:
            self.pixset(x,y,r,g,b)
            return
        if xd>yd:
            if x<x2:
                xp=x
                while xp<=x2:
                    self.pixset(xp,y+(y2-y)*(xp-x)/(x2-x),r,g,b)
                    xp+=1
            if x>=x2:
                xp=x2
                while xp<=x:
                    self.pixset(xp,y2+(y-y2)*(xp-x2)/(x-x2),r,g,b)
                    xp+=1
        if xd<=yd:
            if y<y2:
                yp=y
                while yp<=y2:
                    self.pixset(x+(x2-x)*(yp-y)/(y2-y),yp,r,g,b)
                    yp+=1
            if y>=y2:
                yp=y2
                while yp<=y:
                    self.pixset(x2+(x-x2)*(yp-y2)/(y-y2),yp,r,g,b)
                    yp+=1
    def fix48set(self,x,y,c,r,g,b):
        if c >= 0x20 and c <= 0x7f:
            idx = (c - 0x20)*4
            for i in range(4):
                dat=fix48[idx+i]
                for j in range(4):
                    if dat & 0x80:
                        self.pixset(x+j,y,r,g,b)
                    dat=dat<<1
                y=y+1
                for j in range(4):
                    if dat & 0x80:
                        self.pixset(x+j,y,r,g,b)
                    dat=dat<<1
                y=y+1

    def fix1212set(self,x,y,c,r,g,b):
        if c >= ord('0') and c <= ord('9'):
            fix1212idx=(c-ord('0')+0)*18
        elif c >= ord('A') and c <= ord('Z'):
            fix1212idx=(c-ord('A')+10)*18
        elif c >= ord('a') and c <= ord('z'):
            fix1212idx=(c-ord('a')+36)*18
        else:
            return

        for fx1212i in range(6):
            dat=fix1212[fix1212idx+fx1212i*3]
            for j in range(8):
                if dat & 0x80:
                    self.pixset(x+j,y,r,g,b)
                dat=dat<<1
            dat=fix1212[fix1212idx+fx1212i*3+1]
            for j in range(4):
                if dat & 0x80:
                    self.pixset(x+j+8,y,r,g,b)
                dat=dat<<1
            y=y+1
            for j in range(4):
                if dat & 0x80:
                    self.pixset(x+j,y,r,g,b)
                dat=dat<<1
            dat=fix1212[fix1212idx+fx1212i*3+2]
            for j in range(8):
                if dat & 0x80:
                    self.pixset(x+j+4,y,r,g,b)
                dat=dat<<1
            y=y+1

    def str48set(self,x,y,c,r,g,b,xadd=5,yadd=0):
        strlen=len(c)
        for i in range(strlen):
            self.fix48set(x,y,ord(c[i]),r,g,b)
            x=x+xadd
            y=y+yadd

    def str1212set(self,x,y,c,r,g,b,xadd=12,yadd=0):
        strlen=len(c)
        for i in range(strlen):
            self.fix1212set(x,y,ord(c[i]),r,g,b)
            x=x+xadd
            y=y+yadd

    def drawbmp(self,bmpfile,x,y):
        infile = open(bmpfile, 'rb')
        bmpdat = infile.read()
        bmpsize = len(bmpdat)
        bmptype = bmpdat[0:2]
        bmpofs = ord(bmpdat[10]) + ord(bmpdat[11])*256 + ord(bmpdat[12])*65536 + ord(bmpdat[13])* 16777216
        bmphsz = ord(bmpdat[14]) + ord(bmpdat[15])*256 + ord(bmpdat[16])*65536 + ord(bmpdat[17])* 16777216
        if bmphsz == 40:
            bmpwidth = ord(bmpdat[18]) + ord(bmpdat[19])*256 + ord(bmpdat[20])*65536 + ord(bmpdat[21])* 16777216
            bmpheight = ord(bmpdat[22]) + ord(bmpdat[23])*256 + ord(bmpdat[24])*65536 + ord(bmpdat[25])* 16777216
            bmpbit = ord(bmpdat[28]) + ord(bmpdat[29])*65536
        else:
            bmpwidth = ord(bmpdat[18]) + ord(bmpdat[19])*65536
            bmpheight = ord(bmpdat[20]) + ord(bmpdat[21])* 65536
            bmpbit = ord(bmpdat[24]) + ord(bmpdat[25])*65536

        bmplinsiz=bmpwidth*3
        if (bmplinsiz)%4 != 0:
            bmplinsiz=(bmplinsiz/4)*4+4

        infile.close()

        global xScale
        global yScale
        if fitMode==1:
            xScale=float(scrWidth)/float(bmpwidth)
            yScale=xScale
        elif fitMode==2:
            yScale=float(scrHeight)/float(bmpheight)
            xScale=yScale
        elif fitMode==3:
            xScale=float(scrWidth)/float(bmpwidth)
            yScale=float(scrHeight)/float(bmpheight)

        bmpidx = bmpofs
        bmpspl = bmpwidth%8
        bmpskp=0
        if bmpspl != 0:
            bmpskp=8-bmpspl

        for bmpy in range(int(bmpheight*yScale)):
            for bmpx in range(int(bmpwidth*xScale)):
                bmpidx=((bmpheight-int(bmpy/yScale)-1)*bmplinsiz+int(bmpx/xScale)*3)+bmpofs
                lcd.pixset(bmpx+x,bmpy+y, ord(bmpdat[bmpidx+2]), ord(bmpdat[bmpidx+1]), ord(bmpdat[bmpidx+0]))

if __name__ == "__main__":
    lcd = ILI9340()
    lcd.write_cmd(0x2C)

    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    argc = len(argvs) # 引数の個数

    i = 0
    while (i < argc):
        paraType = ArgCheck(argvs[i], argParaX) # X座標
        if (paraType != -1):
            i = i + 1;
            if (i >= argc):
                break
            else:
                xpos = int(argvs[i])
                i = i + 1;
                continue
        paraType = ArgCheck(argvs[i], argParaY) # Y座標
        if (paraType != -1):
            i = i + 1;
            if (i >= argc):
                break
            else:
                ypos = int(argvs[i])
                i = i + 1;
                continue
        paraType = ArgCheck(argvs[i], argParaRot)   # 画面向き
        if (paraType != -1):
            i = i + 1;
            if (i >= argc):
                break
            else:
                scrrot = int(argvs[i])
                if scrrot==0:
                    scrWidth = c_lcdWidth
                    scrHeight = c_lcdHeight
                elif scrrot==1:
                    scrWidth = c_lcdHeight
                    scrHeight = c_lcdWidth
                elif scrrot==2:
                    scrWidth = c_lcdWidth
                    scrHeight = c_lcdHeight
                elif scrrot==3:
                    scrWidth = c_lcdHeight
                    scrHeight = c_lcdWidth
                else:
                    scrrot=0
                i = i + 1;
                continue
        paraType = ArgCheck(argvs[i], argParaScale) # スケール
        if (paraType != -1):
            if (i + 2 >= argc):
                break
            else:
                xScale = float(argvs[i + 1])
                yScale = float(argvs[i + 2])
                fitMode=0
                i = i + 3
                continue
        paraType = ArgCheck(argvs[i], argParaFit)   # フィット
        if (paraType != -1):
            i = i + 1
            if (i >= argc):
                break
            else:
                paraType = StrCheck(argvs[i], argParaWidth)
                if (paraType != -1):
                    fitMode=1
                    i = i + 1
                    continue
                paraType = StrCheck(argvs[i], argParaHeight)
                if (paraType != -1):
                    fitMode=2
                    i = i + 1
                    continue
                paraType = StrCheck(argvs[i], argParaBoth)
                if (paraType != -1):
                    fitMode=3
                    i = i + 1
                    continue
                fitMode=0
                continue
        paraType = ArgCheck(argvs[i], argParaBmp)   # BMP画像描画
        if (paraType != -1):
            i = i + 1
            if (i >= argc):
                break
            else:
                bmpFile = argvs[i]
                i = i + 1
                lcd.drawbmp(bmpFile,xpos,ypos)
                continue
        paraType = ArgCheck(argvs[i], argParaColor) # 色指定
        if (paraType != -1):
            if (i + 3 >= argc):
                break
            else:
                rColor = int(argvs[i + 1])
                gColor = int(argvs[i + 2])
                bColor = int(argvs[i + 3])
                i = i + 4
                continue
        paraType = ArgCheck(argvs[i], argParaLine)  # ライン描画
        if (paraType != -1):
            if (i + 4 >= argc):
                break
            else:
                x1 = int(argvs[i + 1])
                y1 = int(argvs[i + 2])
                x2 = int(argvs[i + 3])
                y2 = int(argvs[i + 4])
                i = i + 5
                lcd.lineset(x1,y1,x2,y2,rColor,gColor,bColor)
                continue
        paraType = ArgCheck(argvs[i], argParaTextRot)   # テキスト向き
        if (paraType != -1):
            i = i + 1;
            if (i >= argc):
                break
            else:
                rotText = int(argvs[i])
                i = i + 1;
                continue
        paraType = ArgCheck(argvs[i], argParaTextType)  # テキストタイプ
        if (paraType != -1):
            i = i + 1;
            if (i >= argc):
                break
            else:
                typeText = int(argvs[i])
                i = i + 1;
                continue
        paraType = ArgCheck(argvs[i], argParaText)  # テキスト表示
        if (paraType != -1):
            i = i + 1
            if (i >= argc):
                break
            else:
                strText = argvs[i]
                i = i + 1
                if rotText == 0:
                    texXAdd=1
                    texYAdd=0
                elif rotText == 1:
                    texXAdd=0
                    texYAdd=1
                elif rotText == 2:
                    texXAdd=-1
                    texYAdd=0
                elif rotText == 3:
                    texXAdd=0
                    texYAdd=-1
                else:
                    texXAdd=1
                    texYAdd=0
                if typeText == 1:
                    lcd.str1212set(xpos,ypos,strText,rColor,gColor,bColor,texXAdd*12,texYAdd*12)
                else:
                    lcd.str48set(xpos,ypos,strText,rColor,gColor,bColor,texXAdd*5,texYAdd*5)
                continue
        paraType = ArgCheck(argvs[i], argParaHelp)  # ヘルプタイプ
        if (paraType != -1):
            i = i + 1;
            print "gmlpi : GML for Raspberry-PI and ILI9340 LCD on SPI"
            print ver
            print "Usage"
            print "python gmlpi -[Option Data]"
            print ""
            print "Ooption list"
            print "help : this operation"
            print "demo : auto demonstration"
            print "rot : lcs screen rotate data range 0-3 mean 12oclock \/ 3oclock \/ 6oclock \/ 9oclock"
            print "x : draw x position data"
            print "y : draw y position data"
            print "color : rgb 3 datas range 0-255"
            print "line : start x y and end x y 4 data"
            print "textrot : text direction data range 0-3 mean left-right \/ top-bottom \/ right-left \/ bottom-top"
            print "texttype : text size data range 0-1 default 1 mean 4x8 \/ 12x12"
            print "text : text string data range ascii charactor"
            print "scale : graphic scale x y data range float"
            print "fit : graphic scale fit to screen scale data range 3 type command width \/ height \/ both"
            print "bmp : 24bit plane bmp graphoc file load and graw"
            sys.exit(0)
        paraType = ArgCheck(argvs[i], argParaDemo)  # デモタイプ
        if (paraType != -1):
            scrrot=0
            rColor = 255
            gColor = 255
            bColor = 255
            lcd.fill(  0,   0,   0)
            lcd.fill(  0,   0, 255)
            lcd.fill(255,   0,   0)
            lcd.fill(255,   0, 255)
            lcd.fill(  0, 255,   0)
            lcd.fill(  0, 255, 255)
            lcd.fill(255, 255,   0)
            lcd.fill(255, 255, 255)
            time.sleep(2)
            lcd.fill(  0,   0,   0)
            time.sleep(1)
            for i in range(24):
                lcd.lineset(120,160,i*10,0,255*i/24,0x00,0x00)
            lcd.fbtrn()
            for i in range(32):
                lcd.lineset(120,160,239,i*10,0x00,255*i/32,0x00)
            lcd.fbtrn()
            for i in range(24):
                lcd.lineset(120,160,239-i*10,319,0x00,0x00,255*i/24)
            lcd.fbtrn()
            for i in range(32):
                lcd.lineset(120,160,0,319-i*10,255*i/32,255*i/32,255*i/32)
            lcd.fbtrn()
            rotText=0
            typeText=1
            lcd.str1212set(0,0,"GMLPI TEXT DRAW DEMO",255,255,255,12,0)
            lcd.str1212set(228,12," Draw Direction Change  ",255,255,255,0,12)
            lcd.str1212set(228,300,"Right to Left Draw  ",255,255,255,-12,0)
            lcd.str1212set(0,300," Bottom to Top Drawing  ",255,255,255,0,-12)
            lcd.str48set(100,200,"SMALL TEXT",255,255,255,5,0)
            lcd.fbtrn()
            time.sleep(5)
            scrrot=0
            fitMode=0
            xScale=1.0
            yScale=1.0
            lcd.drawbmp("pic00.bmp",0,0)
            lcd.str1212set(0,256,"BMP DRAW DEMO",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            scrrot=1
            lcd.drawbmp("pic00.bmp",0,0)
            scrrot=0
            lcd.str1212set(0,256,"SCREEN ROTATE",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            scrrot=2
            lcd.drawbmp("pic00.bmp",0,80)
            scrrot=0
            lcd.str1212set(0,256,"SCREEN ROTATE",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            scrrot=3
            lcd.drawbmp("pic00.bmp",80,0)
            scrrot=0
            lcd.str1212set(0,256,"SCREEN ROTATE",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            scrrot=0
            fitMode=1
            lcd.drawbmp("pic00.bmp",0,0)
            lcd.str1212set(0,256,"STRECH WIDTH",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            scrrot=0
            fitMode=2
            lcd.drawbmp("pic00.bmp",0,0)
            lcd.str1212set(0,256,"STRECH HEIGHT",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            scrrot=0
            fitMode=3
            lcd.drawbmp("pic00.bmp",0,0)
            lcd.str1212set(0,256,"STRECH BOTH",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            scrrot=0
            lcd.str1212set(40,256,"THANK YOU",255,255,255,12,0)
            lcd.fbtrn()
            time.sleep(2)
            lcd.fill(  0,   0,   0)   # Fill 
            sys.exit(0)
        else:
            i = i + 1

    lcd.fbtrn() # 転送
    exit

