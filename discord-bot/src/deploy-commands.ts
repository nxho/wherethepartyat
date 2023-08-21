import { REST, Routes } from 'discord.js';
import { config } from './config';
import { commands } from './commands';

const commandsData = Object.values(commands).map((command) => command.data);

const rest = new REST({ version: '10' }).setToken(config.DISCORD_TOKEN);

type DeployCommandsProps = {
  guildId: string;
};

export async function deployCommands({ guildId }: DeployCommandsProps) {
  console.log('Started refreshing application (/) commands.');

  await rest.put(Routes.applicationGuildCommands(config.DISCORD_CLIENT_ID, guildId), {
    body: commandsData,
  });

  console.log('Successfully reloaded application (/) commands.');
}

deployCommands({ guildId: config.HHH_GUILD_ID }).catch((e) => {
  console.error(e);
});
