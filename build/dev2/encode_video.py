"""Encode the frames from render_spin_video.py into figures/Resondi-Device-Video.mp4.

Run: python build/dev2/encode_video.py   (needs: pip install imageio-ffmpeg)
Adds a soft vignette like the original clip. H.264, 30 fps, no audio.
"""
import os
import subprocess
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
frames = os.path.join(HERE, "out", "video", "f_%04d.png")
out = os.path.normpath(os.path.join(HERE, "..", "..", "figures", "Resondi-Device-Video.mp4"))
cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-framerate", "30", "-start_number", "1", "-i", frames,
       "-vf", "scale=1920:1080:flags=lanczos,vignette=angle=PI/4.2,format=yuv420p", "-c:v", "libx264", "-crf", "18",
       "-preset", "slow", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True)
print("wrote", out)
