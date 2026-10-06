import cv2
import sys
import random
import numpy as np

def get_deterministic_shuffled_range(n: int, seed: int) -> list[int]:
    """
    Generates a list of integers from 0 to N (inclusive) 
    and deterministically shuffles them using a fixed seed.
    """
    numbers = list(range(n + 1))
    
    # Initialize the PRNG state with a specific seed
    rng = random.Random(seed)
    rng.shuffle(numbers)

    if len(numbers) != len(set(numbers)):
        print("there are duplicates")
    
    return numbers

def interactive_video_trimmer(video_path):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file '{video_path}'")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if fps <= 0 or total_frames <= 0:
        print("Error: Invalid frame or FPS count retrieved from video.")
        return

    print("=" * 60)
    print(f"Loaded: {video_path}")
    print(f"Total Frames: {total_frames} | FPS: {fps:.2f}")
    print("=" * 60)
    print("CONTROLS:")
    print("  Trackbar : Drag to preview any frame")
    print("  'i'      : Set IN point (start frame)")
    print("  'o'      : Set OUT point (end frame)")
    print("  'p'      : Play selected frame range")
    print("  'q'      : Quit")
    print("=" * 60)

    cv2.namedWindow("Video Trimmer")
    
    start_frame = 0
    end_frame = total_frames - 1

    def on_trackbar(val):
        cap.set(cv2.CAP_PROP_POS_FRAMES, val)
        ret, frame = cap.read()
        if ret:
            # Overlay info onto frame preview
            display_frame = frame.copy()
            status_text = f"Frame: {val}/{total_frames - 1} | In: {start_frame} | Out: {end_frame}"
            cv2.putText(display_frame, status_text, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Video Trimmer", display_frame)

    cv2.createTrackbar("Frame", "Video Trimmer", 0, max(1, total_frames - 1), on_trackbar)
    on_trackbar(0)  # Render initial frame

    ret, frame = cap.read()
    height, width, channels = frame.shape
    shuffled_frame = np.zeros((height, width, channels), dtype=np.uint8)
    SEED = 42
    vert_shuffle = get_deterministic_shuffled_range(height-1, SEED)
    hor_shuffle = get_deterministic_shuffled_range(width-1, SEED)

    while True:
        key = cv2.waitKey(0) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('i'):
            start_frame = cv2.getTrackbarPos("Frame", "Video Trimmer")
            if start_frame > end_frame:
                end_frame = start_frame
            print(f"[Marked IN Point]: Frame {start_frame}")
            on_trackbar(start_frame)

        elif key == ord('o'):
            end_frame = cv2.getTrackbarPos("Frame", "Video Trimmer")
            if end_frame < start_frame:
                start_frame = end_frame
            print(f"[Marked OUT Point]: Frame {end_frame}")
            on_trackbar(end_frame)

        elif key == ord('p'):
            print(f"\n▶ Playing selection: frames {start_frame} to {end_frame}...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            delay = int(1000 / fps)

            for f_idx in range(start_frame, end_frame + 1):
                ret, frame = cap.read()
                if not ret:
                    break

                for iv in range(height):
                    for ih in range(width):
                        shuffled_frame[iv][ih][:] = frame[vert_shuffle[iv]][hor_shuffle[ih]][:]

                # Show playback indicator
                cv2.putText(shuffled_frame, f"Playing: {f_idx}/{end_frame}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                cv2.imshow("Video Trimmer", shuffled_frame)

                # Press 'q' or Esc to stop playback midway
                key_playback = cv2.waitKey(delay) & 0xFF
                if key_playback == ord('q') or key_playback == 27:
                    print("Playback stopped.")
                    break

            # Snap back to current trackbar position after playback finishes
            current_pos = cv2.getTrackbarPos("Frame", "Video Trimmer")
            on_trackbar(current_pos)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_file = sys.argv[1]
    else:
        video_file = "input.webm"  # Replace with your video file path

    interactive_video_trimmer(video_file)