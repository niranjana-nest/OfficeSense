from officesense.ingestion.video_source import read_video_frames


video_path = "data/videos/office_video2.mp4"

frame_count = 0

for item in read_video_frames(
    video_path=video_path,
    camera_id="test-camera-01"
):
    frame_count += 1

    print(
        f"Camera: {item['camera_id']} | "
        f"Frame: {item['frame_no']} | "
        f"Timestamp: {item['ts']} | "
        f"Shape: {item['frame'].shape}"
    )

print(f"\nIngestion complete! Total frames sampled: {frame_count}")
