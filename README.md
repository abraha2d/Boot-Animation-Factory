# Boot Animation Factory

### Installation

```bash
pipenv install
pipenv run ./createBootAnimation.py
```

### Usage

- `createBootAnimation.py -np video.mp4`
- Common input options: `1 p 0 0`

```
usage: createBootAnimation.py [-h] [-j JOBS] [-p | -np] [-z | -nz] [-q | -nq]
                              [-ne] [-nc] [-ns] [-v]
                              FILE

positional arguments:
  FILE                  path to the video file to convert

optional arguments:
  -h, --help            show this help message and exit
  -j JOBS, --jobs JOBS  specify number of jobs (commands) to run
                        simultaneously
  -p, --pngcrush        (DEFAULT) use pngcrush (fast, and fairly good
                        compression)
  -np, --no-pngcrush    don't use pngcrush
  -z, --zopfli          use zopfli (very slow, but only marginally better than
                        pngcrush (around 10%)
  -nz, --no-zopfli      (DEFAULT) don't use zopfli
  -q, --pngquant        use pngquant, reduce to 256 colors (may make your boot
                        animation look terrible)
  -nq, --no-pngquant    (DEFAULT) don't use pngquant
  -ne, --no-extract     Don't extract frames from video (use if tmp directory
                        still exists from previous run)
  -nc, --no-config      Don't configure desc.txt (use if it still exists from
                        previous run)
  -ns, --no-select      Don't select frames (use if frames are in proper
                        directories from previous run)
  -v, --version         show program's version number and exit
```

- viewBootAnimation.py

```
usage: viewBootAnimation.py [-h] [FILE]

positional arguments:
  FILE        path to the video file to convert

optional arguments:
  -h, --help  show this help message and exit
```
