
# RTMP


# Streaming with FFMPEG

If not using client.py it is possible to send a stream manually with FFMPEG.
Send stream in RTMP to server on port 1942

"""
ffmpeg -i obama.mp4 -c:v copy -c:a copy -f flv rtmp://127.0.0.1:1942/test/sample

"""

Stream your camera to server with client/client.py

---

# Check Camera/Audio on Linux:

"""v4l2-ctl --list-devices"""

If v4l2 is not installed: 

"""sudo apt-get install v4l-utils"""

For the audio and video: 

"""sudo  arecord -l"""

---

# Remove and Install latest FFMPEG 

To install FFMPEG use: 

"""
sudo apt-get install ffmpeg
"""

If you alaready have an older version and need to remove it:

"""
apt-get remove ffmpeg
add-apt-repository -y ppa:savoury1/ffmpeg4
apt install -y ffmpeg
ffmpeg -version
add-apt-repository --remove ppa:savoury1/ffmpeg4
"""

---

# Install H264 decoder in Ubuntu

The streamed video is saved in H264 codec. Therefore to whatch the video use:

"""
sudo apt install libdvdnav4 libdvd-pkg gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libdvd-pkg
sudo apt-get install ubuntu-restricted-extras
"""

And for Ubuntu 18.04
sudo apt-get install -y libavcodec57

And for Ubuntu 20.04
sudo apt-get install -y libavcodec58


