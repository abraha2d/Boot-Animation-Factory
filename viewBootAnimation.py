#!/usr/bin/env python
import sys
import zipfile
import pygame
from pygame.locals import *
import io

if len(sys.argv) < 2:
    bootanim = zipfile.ZipFile("bootanimation.zip")
else:
    bootanim = zipfile.ZipFile(sys.argv[1])
desc = bootanim.open("desc.txt")
width, height, fps = desc.readline().strip().split(" ")
print "\nSize: " + width + " x " + height + " @ " + fps + "fps"

width = int(width)
height= int(height)
fps = int(fps)
size = width, height

partd = []
partn = {}

for line in desc:
    partd.append(line.strip().split(" "))
    partd[-1][1] = int(partd[-1][1])
    partd[-1][2] = int(partd[-1][2])
    partn[partd[-1][3]] = []

print "Parts: " + str(partn.keys()) + "\n"

namelist = bootanim.namelist()
for i in namelist:
    part = i.split("/")[0]
    if part in partn.keys():
#        print "Loading " + i
        img = pygame.image.load(io.BytesIO(bootanim.read(i)), i)
        partn[part].append(img)

pygame.init()
clock = pygame.time.Clock()
clock.tick(fps)

screen = pygame.display.set_mode(size, RESIZABLE)

toExit = False

def loopdeloop():
    global toExit
    for img in partn[part[3]]:
        screen.blit(img, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYUP and event.key == K_ESCAPE:
                print "Exiting..."
                toExit = True
                if part[0] == 'p':
                    return
        clock.tick(fps)
    for i in xrange(part[2]):
        clock.tick(fps)

for part in partd:
    if part[1] == 0:
        while True:
            loopdeloop()
            if toExit:
                break
    else:
        if part[0] == 'c' or not toExit:
            for i in xrange(part[1]):
                loopdeloop()
