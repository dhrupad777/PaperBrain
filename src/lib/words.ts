import { convertAmountToWords } from "@/ai/flows/amount-in-words-converter";

export async function getAmountInWords(amount: number): Promise<string> {
  if (isNaN(amount) || amount <= 0) {
    return '';
  }
  try {
    const result = await convertAmountToWords({ amount });
    return result.amountInWords;
  } catch (error) {
    console.error("Failed to convert amount to words:", error);
    // Fallback to a simple message or empty string
    return '';
  }
}
