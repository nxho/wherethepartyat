import { Client } from 'discord.js';
import express from 'express';

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

const app = express();
app.get('/healthz', async (_req, res, _next) => {
  const healthcheck = {
    uptime: process.uptime(),
    message: 'OK',
    timestamp: Date.now(),
  };

  try {
    res.send(healthcheck);
  } catch (error) {
    healthcheck.message = error as string;
    res.status(503).send();
  }
});

const PORT = process.env.PORT || 4111;
app.listen(PORT, () => console.log('Healthcheck has started at port ' + PORT));
