#!/usr/bin/env python3

import argparse
import av
import multiprocessing
import os
import progressbar
import shutil
import subprocess
import sys
import time

#----------
# Argparse
#

def fyle(x):
    if not os.path.isfile(x):
        raise argparse.ArgumentTypeError("{0} is not a file".format(x))
    return x

parser = argparse.ArgumentParser()

parser.add_argument("input", type=fyle, metavar="FILE",
                    help="path to the video file to convert")

parser.add_argument("-j", "--jobs", type=int, default=multiprocessing.cpu_count(),
                    help="specify number of jobs (commands) to run simultaneously")

pgroup = parser.add_mutually_exclusive_group()
pgroup.add_argument("-p", "--pngcrush", action="store_true", dest="pngcrush",
                    help="(DEFAULT) use pngcrush (fast, and fairly good compression)")
pgroup.add_argument("-np", "--no-pngcrush", action="store_false", dest="pngcrush",
                    help="don't use pngcrush")

zgroup = parser.add_mutually_exclusive_group()
zgroup.add_argument("-z", "--zopfli", action="store_true", dest="zopfli",
                    help="use zopfli (very slow, but only marginally better than pngcrush (around 10%%)")
zgroup.add_argument("-nz", "--no-zopfli", action="store_false", dest="zopfli",
                    help="(DEFAULT) don't use zopfli")

qgroup = parser.add_mutually_exclusive_group()
qgroup.add_argument("-q", "--pngquant", action="store_true", dest="pngquant",
                    help="use pngquant, reduce to 256 colors (may make your boot animation look terrible)")
qgroup.add_argument("-nq", "--no-pngquant", action="store_false", dest="pngquant",
                    help="(DEFAULT) don't use pngquant")

parser.add_argument("-ne", "--no-extract", action="store_false", dest="extract",
                    help="Don't extract frames from video (use if tmp directory still exists from previous run)")

parser.add_argument("-nc", "--no-config", action="store_false", dest="config",
                    help="Don't configure desc.txt (use if it still exists from previous run)")

parser.add_argument("-ns", "--no-select", action="store_false", dest="select",
                    help="Don't select frames (use if frames are in proper directories from previous run)")

parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.9')

parser.set_defaults(pngcrush=True, zopfli=False, pngquant=False, extract=True, config=True, select=True)

args = parser.parse_args()

#------
# Main
#

try:
    container = av.open(args.input)
except av.AVError:
    print("error: %s is not a valid video file" % args.input)
    sys.exit(2)

videoStream = container.streams.video[0]
fps = int(videoStream.average_rate)
numDigits = len(str(videoStream.frames))

print("\nInfo: %dx%d @ %dfps (%d frames)" % (videoStream.width, videoStream.height, fps, videoStream.frames))

if args.extract:

    print("\nExtrating frames from video...")

    try:
        os.makedirs("tmp")
    except FileExistsError:
        shutil.rmtree("tmp")
        os.makedirs("tmp")

    bar = progressbar.ProgressBar(max_value=videoStream.frames, redirect_stdout=True)
    for packet in bar(container.demux()):
        for frame in packet.decode():
            if type(frame) == av.video.frame.VideoFrame:
                frame.to_image().save(("tmp/%%0%dd.png" % numDigits) % frame.index)

partConfig = {}

if args.config:
    print()
    numParts = 0
    while numParts <= 0:
        try:
            numParts = int(input("How many parts does this boot animation have? "))
            if numParts <= 0:
                raise(ValueError())
        except ValueError:
            print("Please enter a valid, positive number.\n")

    for i in range(numParts):

        partName = "part%d" % i
        print("\nConfiguring %s:" % partName)

        print("\n Types:")
        print("   p -> this part will play unless interrupted by the end of the boot")
        print("   c -> this part will play to completion, no matter what\n")
        type = ""
        while type != "c" and type != "p":
            type = input(" What type is this part? ").lower()
            if type != "c" and type != "p":
                print(" Please enter 'p' or 'c'\n")

        count = -1
        while count < 0:
            try:
                count = int(input(" How many times should this part loop (0 to loop forever until boot is complete)? "))
                if count < 0:
                    raise(ValueError())
            except ValueError:
                print(" Please enter a valid, non-negative number.\n")

        pause = -1
        while pause < 0:
            try:
                pause = int(input(" How many FRAMES to delay after this part ends? "))
                if pause < 0:
                    raise(ValueError())
            except ValueError:
                print(" Please enter a valid, non-negative number.\n")

        path = partName

        rgbHex = input(" (optional) a background color, specified as #RRGGBB: ")
        clock = input(" (optional) the y-coordinate at which to draw the current time (for watches): ")

        partConfig[partName] = [type, count, pause, path, rgbHex, clock]

    print("\nWriting desc.txt...")
    descTxt = open("desc.txt", "w")
    descTxt.write("%d %d %d\n" % (videoStream.width, videoStream.height, fps))
    for part in partConfig.values():
        descTxt.write(("%s %d %d %s %s %s" % tuple(part)).strip() + "\n")
    descTxt.close()

else:
    print("\nReading desc.txt...")
    descTxt = open("desc.txt")
    descTxt.readline()
    for line in descTxt:
        configs = line.strip().split(" ", 5)
        if len(configs) < 4:
            print("Error: Malformed desc.txt. Exiting...")
            sys.exit(1)
        configs[1] = int(configs[1])
        configs[2] = int(configs[2])
        partConfig[configs[3]] = configs
    descTxt.close()

if args.select:
    print("\nOpening frame directory to aid in selecting frames...")
    time.sleep(0.5)
    os.system("open tmp")
    for part in partConfig.keys():
        print("\nSelect frames for %s:" % part)

        startFrame = -1
        while startFrame < 0 or startFrame > videoStream.frames:
            try:
                startFrame = int(input(" Start frame: "))
                if startFrame < 0 or startFrame > videoStream.frames:
                    raise(ValueError())
            except ValueError:
                print(" Please enter a valid frame number (between 0 and %d).\n" % videoStream.frames)

        endFrame = -1
        while endFrame < startFrame or endFrame > videoStream.frames:
            try:
                endFrame = int(input(" End frame: "))
                if endFrame < startFrame or endFrame > videoStream.frames:
                    raise(ValueError())
            except ValueError:
                print(" Please enter a valid frame number (between %d and %d).\n" % (startFrame, videoStream.frames))

        partConfig[part] = [startFrame, endFrame]

    print()
    for part, frames in partConfig.items():
        print("Copying frames for %s..." % part)
        try:
            os.makedirs(part)
        except FileExistsError:
            shutil.rmtree(part)
            os.makedirs(part)
        for i in range(frames[0], frames[1]+1):
            shutil.copy2(("tmp/%%0%dd.png" % numDigits) % i, part)
else:
    for part in partConfig.keys():
        imgs = os.listdir(part)
        startFrame = int(imgs[0][:-4])
        endFrame = int(imgs[-1][:-4])
        partConfig[part] = [startFrame, endFrame]

print("\nApplying selected optimizations...")

def pOpti(fyle, i):
    subprocess.call(["pngcrush", "-warn", fyle, "%s.new" % fyle])
    subprocess.call(["mv", "%s.new" % fyle, fyle])
    return i

#def zOpti(fyle, i):
#    subprocess.call(["zopfli/zopflipng", "-m", "-ow", fyle])
#    return i

def qOpti(fyle, i):
    subprocess.call(["pngquant", fyle, "--ext", ".png", "--force"])
    return i

if args.pngcrush:
    for part, frames in partConfig.items():
        print(" %s -> pngcrush:" % part)
        bar = progressbar.ProgressBar(min_value=0, max_value=frames[1]-frames[0])
        def updateBar(q):
            bar.update(min(bar.value+1, bar.max_value))
        pool = multiprocessing.Pool(processes=args.jobs)
        for i in range(frames[0], frames[1]+1):
            pool.apply_async(pOpti, (("%s/%%0%dd.png" % (part, numDigits)) % i, i - frames[0]), callback=updateBar)
        pool.close()
        pool.join()
        bar.finish()

if args.zopfli:
    print("Not implemented.")
#    for part, frames in partConfig.items():
#        print(" %s -> zopflipng:" % part)
#        bar = progressbar.ProgressBar(min_value=0, max_value=frames[1]-frames[0])
#        pool = multiprocessing.Pool(processes=args.jobs)
#        for i in range(frames[0], frames[1]+1):
#            pool.apply_async(zOpti, (("%s/%%0%dd.png" % (part, numDigits)) % i, i - frames[0]), callback=bar.update)
#        pool.close()
#        pool.join()
#        bar.finish()

if args.pngquant:
    for part, frames in partConfig.items():
        print(" %s -> pngquant:" % part)
        bar = progressbar.ProgressBar(min_value=0, max_value=frames[1]-frames[0])
        def updateBar(q):
            bar.update(min(bar.value+1, bar.max_value))
        pool = multiprocessing.Pool(processes=args.jobs)
        for i in range(frames[0], frames[1]+1):
            pool.apply_async(qOpti, (("%s/%%0%dd.png" % (part, numDigits)) % i, i - frames[0]), callback=updateBar)
        pool.close()
        pool.join()
        bar.finish()

print("\nZipping animation to bootanimation.zip (outside directory)...")
subprocess.call(["zip -0qry -i \*.txt \*.png \*.wav @ ../bootanimation.zip *.txt part*"], shell=True)

print("\nAll done.\n")

