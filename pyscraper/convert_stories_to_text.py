import json
import logging
import os
import traceback
from os.path import abspath
from pathlib import Path

import boto3
import requests
from dotenv import load_dotenv
from events_db import persist_events

load_dotenv()

# secrets
aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
openai_api_key=os.getenv('OPEN_AI_KEY')

system_prompt='''
You will be given raw text, broken up into sections. Each section of raw text represents an event.
Take each section of text and return event details in the following JSON format:
{
  "account: string,
  "name": string,
  "description": string,
  "datetime": string,
  "location": string,
  "event": bool,
}
If the data from the extracted text does not look like an event, set the 'event' field to false.
Otherwise, set the 'event' boolean to true. If the text has some text that appears to be an account or username,
set the 'account' string to that text value. Otherwise, set the 'account' string to an empty string.
'''

static_path = os.getenv('STATIC_PATH') or abspath('../static')
images_path = f'{static_path}/uploads'
processed_path = f'{static_path}/processed'

def upload_stories_to_s3():
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name='us-east-2')
    bucket_name = 'wherethepartyatimgdata'

    logging.info('Starting upload to S3')
    for filename in os.listdir(images_path):
        if os.path.isfile(os.path.join(images_path, filename)):
            file_path = f"{images_path}/{filename}"
            s3_key = filename  # Key (path) in S3 where the file will be stored

            logging.info(f"Uploading file '{file_path}' to '{bucket_name}/{s3_key}'")

            s3.upload_file(file_path, bucket_name, filename)

            logging.info(f"Successfully uploaded file '{file_path}' to '{bucket_name}/{s3_key}'")

            dst_file_path = f"{processed_path}/{filename}"
            os.rename(file_path, dst_file_path)

            logging.info(f"Successfully moved source file from '{file_path}' to '{dst_file_path}'")
    logging.info('Finished upload to S3')

def send_to_gpt(lines):
    # Set up the parameters for the GPT-3.5 request
    user_prompt = ""

    for item in lines:
        user_prompt += item + "\n"

    model = 'gpt-3.5-turbo'
    temperature = 0.5
    max_tokens = 1024

    # Set up the headers and data for the GPT-3.5 request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {openai_api_key}",
    }
    data = {
        'messages': [{
            "role": "system",
            "content": system_prompt,
        }, {
            "role": "user",
            "content": user_prompt,
        }],
        'temperature': temperature,
        'max_tokens': max_tokens,
        'model': model,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    logging.info("GPT JSON response", response.json())

    event = response.json()['choices'][0]['message']['content'].strip()
    return json.loads(event)

def create_presigned_url(bucket_name, object_name, expiration=60000):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name='us-east-2')
    """Generate a presigned URL to share an S3 object"""
    try:
        response = s3.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        "ResponseContentType": "image/jpeg"
                                                        'Key': object_name},
                                                ExpiresIn=expiration)
    except Exception as e:
        logging.error(e)
        return None
    
    # The response contains the presigned URL
    return response

def stories_to_text():
    logging.info('Starting Textract and GPT conversion')

    events = []
    s3 = boto3.resource('s3', region_name='us-east-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    bucket_name = 'wherethepartyatimgdata'

    bucket=s3.Bucket(bucket_name)
    image_keys = [obj.key for obj in bucket.objects.all() if obj.key.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]

    for image in image_keys:
        obj = s3.Object(bucket_name, image)

        # Read the binary data of the image file
        image_bytes = obj.get()['Body'].read()

        # Set up the Textract client with the desired region
        client = boto3.client('textract', region_name='us-east-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # Call the Textract API to extract text from the image
        response = client.detect_document_text(Document={'Bytes': image_bytes})

        # logging.info the extracted text
        lines = []
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                lines.append(item['Text'])

        if lines:
            logging.info(f'Text extracted from image: {image}')
            logging.info('\n'.join(lines))
            try:
                event = send_to_gpt(lines)
                event['account'] = image.split(';')[0]

                # Generate a pre-signed URL for the image
                pre_signed_url = create_presigned_url(bucket_name, image)
                event['image_url'] = pre_signed_url

                events.append(event)
            except Exception as e:
                logging.error(f'Error occurred when sending image text to GPT: {e}')
                traceback.print_exc()
        else:
            logging.info('No text found in the image.')

    logging.info('Finished Textract and GPT conversion')

    return events

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('Starting event generation')

    Path(processed_path).mkdir(parents=True, exist_ok=True)

    upload_stories_to_s3()
    events = stories_to_text()
    logging.info('Received events:', json.dumps(events, indent=2))
    persist_events(events)

    logging.info('Finished event generation')
