from fastapi import APIRouter, File, UploadFile, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.services.video_service import upload_video_service
from app.db.base import get_db

import os
import subprocess
import logging
from multiprocessing import Pool, cpu_count
from typing import List, Tuple
import shutil

router = APIRouter()

@router.get("/")
async def get_videos():
    return {"videos": []}

@router.post("/")
async def upload_video(
    title: str,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return await upload_video_service(title, file, background_tasks, db)



# Directories for uploads and outputs
UPLOAD_DIR = "uploaded_videos"
OUTPUT_DIR = "encoded_videos"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define resolutions
RESOLUTIONS = ["1080p", "720p", "480p"]

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Function to encode video to a specific resolution
def encode_video(args: Tuple[str, str]) -> str:
    video_file, resolution = args
    output_file = os.path.join(OUTPUT_DIR, f"{os.path.splitext(os.path.basename(video_file))[0]}_{resolution}.mp4")

    # Map resolutions to FFmpeg scale
    scale_map = {
        "1080p": "1920:1080",
        "720p": "1280:720",
        "480p": "854:480",
    }

    if resolution not in scale_map:
        raise ValueError(f"Unsupported resolution: {resolution}")

    scale = scale_map[resolution]
    ffmpeg_command = [
        "ffmpeg",
        "-i", video_file,  # Input file
        "-vf", f"scale={scale}",  # Video scaling
        "-c:v", "libx264",  # Codec
        "-preset", "fast",  # Encoding speed
        "-crf", "23",  # Quality factor
        "-y",  # Overwrite output
        output_file,  # Output file
    ]

    try:
        logging.info(f"Processing video: {video_file} at resolution: {resolution}")
        subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return f"Encoded {video_file} to {resolution}"
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "No error message captured."
        logging.error(f"Error encoding {video_file} to {resolution}: {error_message}")
        return f"Error encoding {video_file} to {resolution}"


# Function to process a batch of videos
def process_batch(batch: List[Tuple[str, str]]) -> None:
    with Pool(cpu_count()) as pool:
        results = pool.map(encode_video, batch)
        for result in results:
            logging.info(result)


@router.post("/encode/")
async def encode_videos(files: List[UploadFile] = File(...)):
    video_files = []

    # Save uploaded files locally
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file.file.close()  # Ensure file is properly closed
        video_files.append(file_path)

    if not video_files:
        raise HTTPException(status_code=400, detail="No video files provided.")

    # Prepare tasks for encoding
    tasks = [(video_file, resolution) for video_file in video_files for resolution in RESOLUTIONS]

    # Process tasks in batches
    batch_size = 10
    for i in range(0, len(tasks), batch_size):
        logging.info(f"Processing batch {i // batch_size + 1}")
        process_batch(tasks[i:i + batch_size])

    return {"message": "Encoding started for all videos."}
