'use client';

import html2pdf from 'html2pdf.js';

export const downloadInvoicePDF = (node: HTMLElement, filename: string) => {
  if (!node) return;

  const options = {
    margin: 0,
    filename: `${filename}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 3, useCORS: true },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
  };

  html2pdf().from(node).set(options).save();
};

export const printInvoice = () => {
  window.print();
};
