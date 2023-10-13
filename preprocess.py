import sys
if sys.version_info[0] < 3 and sys.version_info[1] < 2:
    raise Exception("Must be using >= Python 3.2")
from os import listdir, path
if not path.isfile('data/face_detection/s3fd-619a316812.pth'):
    raise FileNotFoundError('Save the s3fd model to face_detection/detection/sfd/s3fd.pth before running this script!')
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import argparse, os, traceback, subprocess
import cv2
from tqdm import tqdm
from glob import glob
import audio
from hparams import hparams as hp
import face_detection

def _progress(generated, to_generate):
    progress((generated, to_generate))

def preprocess_video_files(args):
    fa = [face_detection.FaceAlignment(face_detection.LandmarksType._2D, flip_input=False, device='cpu') for _ in range(args.ngpu)]

    template = 'ffmpeg -loglevel panic -y -i {} -strict -2 {}'

    def process_video_file(vfile, args, gpu_id):
        video_stream = cv2.VideoCapture(vfile)
        frames = []
        while 1:
            still_reading, frame = video_stream.read()
            if not still_reading:
                video_stream.release()
                break
            frames.append(frame)
        vidname = os.path.basename(vfile).split('.')[0]
        dirname = vfile.split('/')[-2]
        fulldir = path.join(args.preprocessed_root, dirname, vidname)
        os.makedirs(fulldir, exist_ok=True)
        batches = [frames[i:i + args.batch_size] for i in range(0, len(frames), args.batch_size)]
        i = -1
        for fb in tqdm(batches, desc='Processing Video Frames'):
            preds = fa[gpu_id].get_detections_for_batch(np.asarray(fb))
            for j, f in enumerate(preds):
                i += 1
                if f is None:
                    continue
                x1, y1, x2, y2 = f
                cv2.imwrite(path.join(fulldir, '{}.jpg'.format(i)), fb[j][y1:y2, x1:x2])
                _progress(i + 1, len(batches) * args.batch_size)

    def process_audio_file(vfile, args):
        vidname = os.path.basename(vfile).split('.')[0]
        dirname = vfile.split('/')[-2]
        fulldir = path.join(args.preprocessed_root, dirname, vidname)
        os.makedirs(fulldir, exist_ok=True)
        wavpath = path.join(fulldir, 'audio.wav')
        command = template.format(vfile, wavpath)
        subprocess.call(command, shell=True)
        _progress(1, 1)

    def mp_handler(job):
        vfile, args, gpu_id = job
        try:
            process_video_file(vfile, args, gpu_id)
        except KeyboardInterrupt:
            exit(0)
        except:
            traceback.print_exc()

    print('Started processing for {} with {} GPUs'.format(args.data_root, args.ngpu))
    filelist = glob(path.join(args.data_root, '*.mp4'))
    
    jobs = [(vfile, args, i % args.ngpu) for i, vfile in enumerate(filelist)]
    p = ThreadPoolExecutor(args.ngpu)
    futures = [p.submit(mp_handler, j) for j in jobs]
    _ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]
    
    print('Dumping audios...')
    
    for vfile in tqdm(filelist):
        try:
            process_audio_file(vfile, args)
            _progress(1, 1)
        except KeyboardInterrupt:
            exit(0)
        except:
            traceback.print_exc()
            continue

def main(args):
    print('Started processing for {} with {} GPUs'.format(args.data_root, args.ngpu))
    filelist = glob(path.join(args.data_root, '*.mp4'))

    jobs = [(vfile, args, i % args.ngpu) for i, vfile in enumerate(filelist)]
    p = ThreadPoolExecutor(args.ngpu)
    futures = [p.submit(mp_handler, j) for j in jobs]
    _ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]
    _progress(1, 1)

print('Dumping audios...')
for vfile in tqdm(filelist, desc='Processing Audio Files'):
    try:
        process_audio_file(vfile, args)
    except KeyboardInterrupt:
        exit(0)
    except:
        traceback.print_exc()
        continue
    _progress(1, len(filelist))

if __name__ == '__main__':
    main(args)