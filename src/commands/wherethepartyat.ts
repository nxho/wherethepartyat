import { CommandInteraction, SlashCommandBuilder } from 'discord.js';
import fs from 'node:fs';
import { config } from '../config';

export const data = new SlashCommandBuilder()
  .setName('wherethepartyat')
  .setDescription('Where the party at?');

export async function execute(interaction: CommandInteraction) {
  await interaction.deferReply();

  // Send a message into the channel where command was triggered from
  // const inviteText = await nathanielIsSuperSmart();
  const data = fs.readFileSync('invites/invite.txt');
  console.log('data', data.toString());

  const ai_headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${config.OPEN_AI_KEY}`,
  };
  const model = 'gpt-3.5-turbo';
  const temperature = 0.5;
  const maxTokens = 1024;

  const ai_data = {
    messages: [
      {
        role: 'system',
        content: `Take this text data of events happening nearby and return a random selection of 5 events close to the current time`,
      },
      {
        role: 'user',
        content: data.toString('utf-8'),
      },
    ],
    temperature: temperature,
    max_tokens: maxTokens,
    model: model,
  };

  try {
    console.log('before fetch');
    // Send the GPT-3.5 request using the axios library
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: ai_headers,
      body: JSON.stringify(ai_data),
    });

    // Convert the response to a JSON object
    const responseData = await response.json();
    console.log('responsedata', responseData);

    // Extract the generated calendar invite from the GPT-3.5 response
    const events = responseData.choices[0].message.content.trim();
    console.log('events', events);

    await interaction.editReply(events);
  } catch (error) {
    console.log(error);
    await interaction.editReply('Oops! Something went wrong.');
  }
}
