import dotenv from 'dotenv';

dotenv.config();

const {
  DISCORD_TOKEN,
  DISCORD_CLIENT_ID,
  OPEN_AI_KEY,
  AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY,
  HHH_GUILD_ID,
  EVENTS_DB_PATH,
} = process.env;

if (
  !DISCORD_TOKEN ||
  !DISCORD_CLIENT_ID ||
  !OPEN_AI_KEY ||
  !AWS_ACCESS_KEY_ID ||
  !AWS_SECRET_ACCESS_KEY ||
  !HHH_GUILD_ID
) {
  throw new Error('Missing environment variables');
}

export const config = {
  DISCORD_TOKEN,
  DISCORD_CLIENT_ID,
  OPEN_AI_KEY,
  AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY,
  HHH_GUILD_ID,
  EVENTS_DB_PATH,
};
