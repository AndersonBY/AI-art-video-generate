# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-02-01 18:07:55
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-02-11 13:39:40
from pathlib import Path

import librosa
from skimage.io import imread
from skimage.filters import gaussian
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, ImageClip


BGM_MUSIC = "./bgm.mp3"
WIDTH, HEIGHT = 1920, 1080

FOOTAGES_FOLDER_PATHS = {
    "孙悟空-剪纸风": "./footages/paper-cut-sunwukong-upscaled/",
    "白骨精-剪纸风": "./footages/paper-cut-lady-white-bone-upscaled/",
    "兔子-剪纸风": "./footages/paper-cut-rabbit-upscaled/",
    "兔子-折纸风": "./footages/origami-rabbit-upscaled/",
}

y, sr = librosa.load(BGM_MUSIC)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
beat_times = list(librosa.frames_to_time(beats, sr=sr))
print(f"Beats count: {len(beat_times)}")

images = list(Path("./footages").glob("**/*.png"))
images_count = images

clips = []
clip_start_time = 0
start_index = 0
beat_time_index = 0

for name, folder_path in FOOTAGES_FOLDER_PATHS.items():
    print(f"Processing {name}...")
    images = list(Path(folder_path).glob("*.png"))
    images_count = len(images)
    current_batch_beat_times = beat_times[beat_time_index : beat_time_index + images_count * 2]
    for index, beat_time in enumerate(current_batch_beat_times):
        if index % 2 != 0 and index > 0:
            continue
        print(f"{beat_time_index + index}/{len(beat_times)}", images[index // 2])
        image_path = str(images[index // 2])
        image_clip = ImageClip(image_path).set_start(clip_start_time).set_end(current_batch_beat_times[index + 1])
        image_clip = image_clip.set_pos("center")
        blurred_image = gaussian(imread(image_path).astype(float), sigma=20)
        blurred_image_clip = (
            ImageClip(blurred_image)
            .set_start(clip_start_time)
            .set_end(current_batch_beat_times[index + 1])
            .resize(width=WIDTH)
            .set_pos("center")
        )
        clips.append(blurred_image_clip)
        clips.append(image_clip)

        text_clip = (
            TextClip(str(start_index + index // 2), fontsize=32, color="white")
            .set_start(clip_start_time)
            .set_end(current_batch_beat_times[index + 1])
            .set_pos((WIDTH - 60, HEIGHT - 50))
        )
        clips.append(text_clip)

        clip_start_time = current_batch_beat_times[index + 1]

    name_text_clip = (
        TextClip(name, fontsize=64, color="white", font="./fonts/优设标题黑.ttf")
        .set_start(beat_times[max(beat_time_index - 1, 0)])
        .set_end(current_batch_beat_times[-1])
        .set_pos((20, 20))
    )
    clips.append(name_text_clip)

    beat_time_index += images_count * 2
    start_index += images_count

video_clip = CompositeVideoClip(clips, size=(WIDTH, HEIGHT))
audio_clip = AudioFileClip(BGM_MUSIC)
final_clip = video_clip.set_audio(audio_clip)
final_clip = final_clip.set_duration(min(video_clip.duration, audio_clip.duration))
final_clip = final_clip.fadeout(2)
final_clip.audio = final_clip.audio.audio_fadeout(4)
final_clip.write_videofile(
    "output.mp4",
    fps=60,
    codec="h264",
    audio_codec="libmp3lame",
    threads=4,
)
