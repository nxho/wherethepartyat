import { Client } from 'discord.js';

import { config } from './config';
import { commands } from './commands';

console.log('Bot is starting...');

const client = new Client({
  intents: [],
});

client.once('ready', () => {
  console.log('Discord bot is ready! 🤖');
});

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isCommand()) {
    return;
  }
  const { commandName } = interaction;
  if (commands[commandName as keyof typeof commands]) {
    commands[commandName as keyof typeof commands].execute(interaction);
  }
});

client.login(config.DISCORD_TOKEN);
