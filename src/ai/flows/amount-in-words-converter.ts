'use server';

/**
 * @fileOverview Converts a numerical amount to its equivalent in words, especially for invoice totals.
 *
 * - convertAmountToWords - A function that converts a numerical amount to words.
 * - ConvertAmountToWordsInput - The input type for the convertAmountToWords function.
 * - ConvertAmountToWordsOutput - The return type for the convertAmountToWords function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const ConvertAmountToWordsInputSchema = z.object({
  amount: z
    .number()
    .describe('The numerical amount to convert to words. Must be non-negative.'),
});
export type ConvertAmountToWordsInput = z.infer<typeof ConvertAmountToWordsInputSchema>;

const ConvertAmountToWordsOutputSchema = z.object({
  amountInWords: z
    .string()
    .describe('The amount in words, formatted for an invoice.  If the amount is zero, this should be the empty string.'),
});
export type ConvertAmountToWordsOutput = z.infer<typeof ConvertAmountToWordsOutputSchema>;

export async function convertAmountToWords(
  input: ConvertAmountToWordsInput
): Promise<ConvertAmountToWordsOutput> {
  return convertAmountToWordsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'convertAmountToWordsPrompt',
  input: {schema: ConvertAmountToWordsInputSchema},
  output: {schema: ConvertAmountToWordsOutputSchema},
  prompt: `You are an expert in converting numbers to words for invoices, especially in the Indian numbering system (crore, lakh, thousand).

  Given the amount: {{{amount}}}, your task is to convert it into words.

  Instructions:
  1. Use the Indian numbering system (crores, lakhs, thousands) for amounts greater than 99,999.
  2. Ensure that the output is suitable for placement on an invoice.
  3. If the amount is zero, return an empty string.

  Output:`,
});

const convertAmountToWordsFlow = ai.defineFlow(
  {
    name: 'convertAmountToWordsFlow',
    inputSchema: ConvertAmountToWordsInputSchema,
    outputSchema: ConvertAmountToWordsOutputSchema,
  },
  async input => {
    if (input.amount === 0) {
      return {amountInWords: ''};
    }
    const {output} = await prompt(input);
    return output!;
  }
);
