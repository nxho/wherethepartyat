import { S3 } from '@aws-sdk/client-s3';
import { Textract } from '@aws-sdk/client-textract';
import axios from 'axios';
import fs from 'node:fs';
import path from 'node:path';

import { config } from './config';

async function sendToGPT(lines: string[]) {
  // Set up the parameters for the GPT-3.5 request
  let prompt = '';

  for (const item of lines) {
    prompt += item + '\n';
  }

  const model = 'gpt-3.5-turbo';
  const temperature = 0.5;
  const maxTokens = 1024;

  // Set up the headers and data for the GPT-3.5 request
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${config.OPEN_AI_KEY}`,
  };

  const data = {
    messages: [
      {
        role: 'system',
        content: `Take the text data given to you and return event details`,
      },
      {
        role: 'user',
        content: prompt,
      },
    ],
    temperature: temperature,
    max_tokens: maxTokens,
    model: model,
  };

  // Send the GPT-3.5 request using the axios library
  const response = await axios.post('https://api.openai.com/v1/chat/completions', data, {
    headers: headers,
  });

  // Extract the generated calendar invite from the GPT-3.5 response
  const invite = response.data.choices[0].message.content.trim();
  writeToLocalDirectory(invite);
  return invite;
}

function writeToLocalDirectory(invite: string) {
  const fileName = path.resolve('invites/invite.txt');

  fs.appendFileSync(fileName, invite + '\n');
  console.log(`Successfully wrote data to ${fileName}`);
}

export const ocrAndProcess = async () => {
  const s3 = new S3({ region: 'us-east-2' });
  const bucketName = 'wherethepartyatimgdata';

  // Get the S3 object keys that contain the image
  const bucketObjects = await s3.listObjects({ Bucket: bucketName });
  const imageKeys = bucketObjects.Contents?.filter(
    (obj) =>
      obj.Key?.toLowerCase().endsWith('.jpg') ||
      obj.Key?.toLowerCase().endsWith('.jpeg') ||
      obj.Key?.toLowerCase().endsWith('.png') ||
      obj.Key?.toLowerCase().endsWith('.bmp') ||
      obj.Key?.toLowerCase().endsWith('.gif')
  ).map((obj) => obj.Key) as string[];

  for (const image of imageKeys) {
    const object = await s3.getObject({ Bucket: bucketName, Key: image });

    // Read the binary data of the image file
    const imageBytes = await object.Body?.transformToByteArray();

    // Set up the Textract client with the desired region
    const textract = new Textract({ region: 'us-east-2' });

    // Call the Textract API to extract text from the image
    try {
      const response = await textract.detectDocumentText({ Document: { Bytes: imageBytes } });

      // Print the extracted text
      const lines = response.Blocks?.filter((item) => item.BlockType === 'LINE').map(
        (item) => item.Text
      ) as string[];

      if (lines.length > 0) {
        console.log('Text extracted from image:');
        console.log(lines.join('\n'));
        await sendToGPT(lines);
      } else {
        console.log('No text found in the image.');
      }
    } catch (error) {
      console.log(`Error processing image: ${error}`);
      throw error;
    }
  }
};
