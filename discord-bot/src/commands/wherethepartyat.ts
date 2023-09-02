import { CommandInteraction, SlashCommandBuilder } from 'discord.js';
import * as sqlite3 from 'sqlite3';
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

const db = new sqlite3.Database(eventsDbPath, sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to the database');
  }
});

const fetchAllEvents = (): Promise<Event[]> => {
  return new Promise((resolve, reject) => {
    const query = 'SELECT * FROM events ORDER BY RANDOM() limit 5';
    db.all(query, [], (err, rows) => {
      if (err) {
        console.error('Error executing query:', err.message);
        reject(err.message);
      } else {
        // Process the retrieved rows
        console.log('Query result:', rows);
        resolve(rows as Event[]);
      }
    });
  });
};

export const data = new SlashCommandBuilder()
  .setName('wherethepartyat')
  .setDescription('Where the party at?');

export async function execute(interaction: CommandInteraction) {
  await interaction.deferReply();

  try {
  const events = await fetchAllEvents();
  const reply = events.map((e) => {
    const eventName = e.name || "Untitled Event :)";
    const eventDescription = e.description || "?";
    const eventAccount = e.account || "?";
    const eventLocation = e.location || "?";
    const eventDatetime = e.datetime || "?";
  
    return `Event: ${eventName}\n💬${eventDescription}\n🗣️${eventAccount}\n📍${eventLocation}\n📆${eventDatetime}`;
  }).join('\n\n');
  
  await interaction.editReply(reply);
  } catch (error) {
    console.error('Error:', error);
    await interaction.editReply('An error occurred while fetching events.');
  } finally {
    // Close the database connection
    db.close((err) => {
      if (err) {
        console.error('Error closing database:', err.message);
      } else {
        console.log('Database connection closed');
      }
    });
  }
}
