def download_file_from_s3(s3_url, local_path):
    """
    Download a file from S3 to a local path.
    """
    response = requests.get(s3_url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors
    with open(local_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Downloaded file from {s3_url} to {local_path}")


def encode_video(local_path):
    """
    Encode the video into multiple resolutions using FFmpeg.
    """
    resolutions = ["1080p", "720p", "480p", "240p"]
    encoded_files = []

    for resolution in resolutions:
        output_file = f"{local_path.split('.')[0]}_{resolution}.mp4"
        ffmpeg_command = [
            "ffmpeg", "-i", local_path,
            "-vf", f"scale=-2:{resolution.split('p')[0]}",
            output_file
        ]
        subprocess.run(ffmpeg_command, check=True)
        encoded_files.append(output_file)
        print(f"Encoded video at {resolution}: {output_file}")

    return encoded_files


def upload_files_to_s3(files):
    """
    Upload multiple files to S3 and return their URLs.
    """
    s3_urls = {}
    for file in files:
        s3_key = os.path.basename(file)
        with open(file, "rb") as f:
            s3_client.upload_fileobj(f, S3_BUCKET_NAME, s3_key)
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        resolution = s3_key.split('_')[-1].replace('.mp4', '')
        s3_urls[resolution] = s3_url
        print(f"Uploaded {file} to S3: {s3_url}")
    return s3_urls


def poll_sqs():
    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,  # Batch size
                WaitTimeSeconds=10       # Long polling
            )
            messages = response.get("Messages", [])
            for message in messages:
                # Parse the message
                body = json.loads(message["Body"])
                video_id = body["video_id"]
                s3_url = body["s3_url"]

                # Step 1: Download the video from S3
                local_file = f"/tmp/{os.path.basename(s3_url)}"
                download_file_from_s3(s3_url, local_file)

                # Step 2: Encode the video
                encoded_files = encode_video(local_file)

                # Step 3: Upload the encoded files back to S3
                s3_urls = upload_files_to_s3(encoded_files)

                # Step 4: Delete the SQS message after processing
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message["ReceiptHandle"]
                )

                # Cleanup temporary files
                os.remove(local_file)
                for file in encoded_files:
                    os.remove(file)

        except Exception as e:
            print(f"Error processing message: {e}")

        time.sleep(2)  # Avoid overloading the SQS queue


if __name__ == "__main__":
    print("Worker started. Polling SQS...")
    poll_sqs()