from fastapi import UploadFile


async def save_file(temp_file_path: str, file: UploadFile):
    """Save an uploaded file temporarily."""
    with open(temp_file_path, "wb") as temp_file:
        content = await file.read()
        temp_file.write(content)
