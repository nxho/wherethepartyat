from dotenv import load_dotenv
import boto3
import os
import requests
from events_db import persist_events
import json
import traceback
from os.path import abspath

load_dotenv()

# secrets
aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
openai_api_key=os.getenv('OPENAI_API_KEY')

system_prompt='''
You will be given raw text, broken up into sections. Each section of raw text represents an event.
Take each section of text and return event details in the following JSON format:
{
  "name": string,
  "description": string,
  "datetime": string,
  "location": string,
  "event": bool,
}
If the data from the extracted text does not look like an event, set the 'event' field to false.
Otherwise, set the 'event' boolean to true.
'''

images_path = os.getenv('IMAGES_PATH') or abspath('../static/uploads')

def upload_stories_to_s3():
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name='us-east-2')
    bucket_name = 'wherethepartyatimgdata'

    for filename in os.listdir(images_path):
        if os.path.isfile(os.path.join(images_path, filename)):
            file_path = f"{images_path}/{filename}"
            s3_key = filename  # Key (path) in S3 where the file will be stored

            print(f"Uploading file '{file_path}' to '{bucket_name}/{s3_key}'")

            s3.upload_file(file_path, bucket_name, filename)

            print(f"Successfully uploaded file '{file_path}' to '{bucket_name}/{s3_key}'")

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

    event = response.json()['choices'][0]['message']['content'].strip()
    return json.loads(event)

def stories_to_text():
    events = []
    try:
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

            # Print the extracted text
            lines = []
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    lines.append(item['Text'])

            if lines:
                print(f'Text extracted from image: {image}')
                print('\n'.join(lines))
                event = send_to_gpt(lines)
                event['account'] = image.split(';')[0]
                events.append(event)
            else:
                print('No text found in the image.')
    except Exception as e:
        print(f'Error processing image: {e}')
        traceback.print_exc()

    return events

if __name__ == "__main__":
    upload_stories_to_s3()
    events = stories_to_text()
    print('Received events:', json.dumps(events, indent=2))
    persist_events(events)
