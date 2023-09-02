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
    const query = 'SELECT * FROM events limit 5';
    db.all(query, [], (err, rows) => {
      if (err) {
        console.error('Error executing query:', err.message);
        reject(err.message);
      } else {
        // Process the retrieved rows
        console.log('Query result:', rows);
        resolve(rows as Event[]);
      }

      // Close the database connection
      db.close((err) => {
        if (err) {
          console.error('Error closing database:', err.message);
          reject(err.message);
        } else {
          console.log('Database connection closed');
        }
      });
    });
  });
};

export const data = new SlashCommandBuilder()
  .setName('wherethepartyat')
  .setDescription('Where the party at?');

export async function execute(interaction: CommandInteraction) {
  await interaction.deferReply();

  const events = await fetchAllEvents();
  const reply = events.map((e) => {
    const pretty_events = {
      name: e.name,
      value: `💬${e.description}\n📍${e.location}\n📆${e.datetime}`,
    };

    return pretty_events;

  })

  await interaction.editReply(JSON.stringify(reply,null,2));
}
