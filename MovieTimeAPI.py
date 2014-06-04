from flask import *
import subprocess
import signal
import os
import fnmatch

app = Flask(__name__)

config = type('ConfigObject', (object, ), {})
config.ffmpeg_process = None
config.current_video_path = None
config.is_video_paused = False
config.video_library = dict()

@app.route('/start')
def start():
   subprocess.call(['killall','ffmpeg'])
   if config.ffmpeg_process:
        config.ffmpeg_process = None
   run_parameters = ["./ffmpeg", "-re", "-i", config.current_video_path, "-af", "volume=1.9", "-vcodec", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-acodec", "aac", "-strict", "experimental", "-ab", "512k", "-f", "flv", "rtmp://127.0.0.1:1935/videos/mv"]
   config.ffmpeg_process = subprocess.Popen(run_parameters)

   return jsonify(error=False, message="ffmpeg started")

@app.route('/pause')
def pause():
   if config.ffmpeg_process:
    if not config.is_video_paused:
      config.ffmpeg_process.send_signal(signal.SIGSTOP)
      config.is_video_paused = True
      return jsonify(error=False, message="ffmpeg paused")

    config.ffmpeg_process.send_signal(signal.SIGCONT)
    config.is_video_paused = False
    return jsonify(error=False, message="ffmpeg unpaused")

   return jsonify(error=True, message="ffmpeg not running")

@app.route('/stop')
def stop():
   if config.ffmpeg_process and not config.ffmpeg_process.poll():
    while not config.ffmpeg_process.poll():
      config.ffmpeg_process.kill()
      return jsonify(error=False, message="ffmpeg stopped")
   return jsonify(error=True, message="ffmpeg not running")

@app.route('/videos')
def show_videos():
  types = ('*.mkv', '*.mp4', '*.avi')
  vid_list = []

  for filetype in types:
    vid_list.extend(os.path.join(dirpath, f)
      for dirpath, dirnames, files in os.walk('.')
      for f in fnmatch.filter(files, filetype))

  config.video_library = dict(enumerate(vid_list))
  return jsonify(videos=config.video_library)

@app.route('/videos/<int:video_number>')
def change_video(video_number):
   if not config.ffmpeg_process:
    if video_number in config.video_library:
      config.current_video_path = config.video_library[video_number]
      return jsonify(error=False, message="video changed to {}".format(config.video_library[video_number]))

    return jsonify(error=True, message="{} not in video library".format(video_number))
   return jsonify(error=True, message="cannot change currently running video")

if __name__ =='__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)