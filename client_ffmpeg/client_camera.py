
#------------------------------------------------------------

import subprocess as sp
import cv2
import pyaudio

rtmp_url = "rtmp://127.0.0.1:1942/test/sample"  # Use localhost for testing

cap = cv2.VideoCapture(0) # uses localhost camera
# Get video information
fps = int(cap.get(cv2.CAP_PROP_FPS))
print ("----> Using frames: " + str(fps))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Get audio Information
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
audio = pyaudio.PyAudio()
audiostream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)


# Start the TCP server first, before the sending client (for testing).
ffplay_process = sp.Popen(['ffplay', '-listen', '1', '-i', rtmp_url])  # Use FFplay sub-process for receiving the RTMP video.

# ffmpeg command
command = ['ffmpeg',
        '-y',
        '-re', # '-re' is requiered when streaming in "real-time"
        '-f', 'rawvideo',
        #'-thread_queue_size', '1024',  # May help https://stackoverflow.com/questions/61723571/correct-usage-of-thread-queue-size-in-ffmpeg
        '-vcodec','rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', "{}x{}".format(width, height),
        '-r', str(fps),
        '-i', '-',
        #'-vn', '-i', camera_path,  # Get the audio stream without using OpenCV, use microphone in the future
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-c:a', 'aac',  # Select audio codec
        '-bufsize', '64M',  # Buffering is probably required
        '-f', 'flv', 
        rtmp_url]

# Pipeline configuration
p = sp.Popen(command, stdin=sp.PIPE)

# read webcamera
while (cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        print("End of input file")
        break

    # write to pipe
    p.stdin.write(frame.tobytes())

p.stdin.close()  # Close stdin pipe
p.wait()

ffplay_process.kill()  # Forcefully close FFplay sub-process
