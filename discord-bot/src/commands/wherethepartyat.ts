import { CommandInteraction, SlashCommandBuilder } from 'discord.js';
import Database from 'better-sqlite3';
import { resolve } from 'node:path';
import { config } from '../config';

interface Event {
  id: number;
  name: string;
  description: string;
  datetime: string;
  location: string;
  account: string;
  image_url: string;
}

const eventsDbPath = config.EVENTS_DB_PATH ?? resolve(__dirname, '../../../events_database.db');

const db = new Database(eventsDbPath, {
  readonly: true,
});

const fetchAllEvents = (): Event[] => {
  const stmt = db.prepare('SELECT * FROM events ORDER BY RANDOM() limit 5');
  return stmt.all() as Event[];
};

export const data = new SlashCommandBuilder()
  .setName('wherethepartyat')
  .setDescription('Where the party at?');

export async function execute(interaction: CommandInteraction) {
  try {
    await interaction.deferReply();

    const events = fetchAllEvents();
    const reply = events
      .map((e) => {
        const eventName = e.name || 'Untitled Event :)';
        const eventDescription = e.description || '?';
        const eventAccount = e.account || '?';
        const eventLocation = e.location || '?';
        const eventDatetime = e.datetime || '?';
        const image_url= e.image_url || 'I have no idea where we got this event from actually';

        return `Event: ${eventName}\n💬${eventDescription}\n🗣️${eventAccount}\n📍${eventLocation}\n📆${eventDatetime}\n🔗${image_url}`;
      })
      .join('\n\n');

    await interaction.editReply(reply);
  } catch (e) {
    console.error('Error occurred for /wherethepartyat', e);
    await interaction.editReply('Something went super wrong!');
  }
}

process.on('exit', () => db.close());
process.on('SIGHUP', () => process.exit(128 + 1));
process.on('SIGINT', () => process.exit(128 + 2));
process.on('SIGTERM', () => process.exit(128 + 15));
