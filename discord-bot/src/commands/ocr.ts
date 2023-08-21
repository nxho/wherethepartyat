import { CommandInteraction, SlashCommandBuilder } from 'discord.js';
import { ocrAndProcess } from '../ocrAndProcess';

export const data = new SlashCommandBuilder()
  .setName('ocr')
  .setDescription('[debug] OCR and process images');

export async function execute(interaction: CommandInteraction) {
  await interaction.deferReply();
  try {
    await ocrAndProcess();
    await interaction.editReply('Success!');
  } catch (e) {
    console.log('Error occurred when running OCR.', e);
    await interaction.editReply('Failed.');
  }
}
