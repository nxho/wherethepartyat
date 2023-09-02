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

        return `Event: ${eventName}\n💬${eventDescription}\n🗣️${eventAccount}\n📍${eventLocation}\n📆${eventDatetime}`;
      })
      .join('\n\n');

    await interaction.editReply(reply);
  } catch (e) {
    console.error('Error occurred for /wherethepartyat', e);
    await interaction.editReply('Something went super wrong!');
  }
}
