'use client';

export const downloadInvoicePDF = async (node: HTMLElement, filename: string) => {
  if (!node) return;

  // Dynamically import html2pdf.js only on the client side
  const html2pdf = (await import('html2pdf.js')).default;

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
