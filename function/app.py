import os
import traceback
import uuid
import boto3
import asyncio
import json

from builders import ImageBuilder

# Initialize S3 client
s3_client = boto3.client('s3')

S3_BUCKET = os.environ.get('S3_BUCKET')


def upload_to_s3(file_path: str, bucket: str, key: str) -> str:
    """
    Uploads a file to S3 and returns the object key or URL.

    :param file_path: Path to the file to upload.
    :param bucket: S3 bucket name.
    :param key: S3 object key.
    :return: S3 object key or URL.
    """
    try:
        s3_client.upload_file(file_path, bucket, key)
        return key
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise e


current_dir = os.getcwd()


def handler(event, context):
    for record in event.get('Records', []):
        try:
            body = record.get('body')
            message = json.loads(body)

            # Extract required fields
            text = message['text']

            # font_path = os.path.join(current_dir, "assets/font")

            builder = ImageBuilder(
                template_name="question.html",
                directory="/tmp"
            )

            # Build the image
            image_file = asyncio.run(
                builder.build(
                    file_name=f"image_{uuid.uuid4().hex[:10]}",
                    context={
                        "text": text,
                    }
                )
            )

            s3_key = f"post-images/{os.path.basename(image_file)}"
            upload_to_s3(image_file, S3_BUCKET, s3_key)

        except Exception as e:
            # Log the error with details
            print(f"Error processing message ID {record.get('messageId')}: {str(e)}")
            print(traceback.format_exc())

    return {}
