/**
 * Formats a number into the Indian numbering system (lakhs, crores).
 * @param value The number to format.
 * @returns A string representing the formatted number.
 */
export function fmt(value: number | string | undefined | null): string {
  const num = Number(value);
  if (isNaN(num)) {
    return '0.00';
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

/**
 * Formats a number as a percentage string.
 * @param value The number to format.
 * @returns A string with the number followed by a '%' sign.
 */
export function pct(value: number | string | undefined | null): string {
  const num = Number(value);
  if (isNaN(num) || num === 0) {
    return '';
  }
  return `${num}%`;
}
