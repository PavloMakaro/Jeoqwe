import subprocess
import os
import sys

def run_ffmpeg_extract(video_path, output_path, time_val):
    """Helper to run ffmpeg command for a specific time."""
    cmd = [
        "ffmpeg",
        "-ss", str(time_val),
        "-i", video_path,
        "-frames:v", "1",
        "-y",
        output_path
    ]
    # Run ffmpeg, suppress output unless error
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0 and os.path.exists(output_path), result.stderr

def extract_frame(video_path, output_path='frame.jpg', frame_time=2):
    """
    Extracts a frame from the video at the specified time (in seconds) using ffmpeg.
    Replaces the previous implementation that used opencv (cv2).
    Includes fallback to frame 0 if specific time fails.
    """
    try:
        # Check if file exists
        if not os.path.exists(video_path):
            return f"Файл не найден: {video_path}"

        # Try specific time
        success, error = run_ffmpeg_extract(video_path, output_path, frame_time)

        if success:
            return f"Кадр сохранен как {output_path}"

        # Fallback to time 0
        success, error_0 = run_ffmpeg_extract(video_path, output_path, 0)

        if success:
            return f"Кадр сохранен как {output_path} (fallback to 0s)"

        # If both failed
        return f"Не удалось извлечь кадр: {error}"

    except Exception as e:
        return f"Ошибка: {str(e)}"

if __name__ == "__main__":
    # Test function
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "test_video.mp4"

    print(f"Extracting frame from {video_path}...")
    result = extract_frame(video_path)
    print(result)
