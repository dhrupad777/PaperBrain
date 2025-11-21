import { z } from 'zod';
import { format } from 'date-fns';

const emptyStringToUndefined = z.literal('').transform(() => undefined);

const numberOrEmptyString = z.union([
  z.number(),
  z.string().refine(val => val === '' || !isNaN(Number(val)), {
    message: "Must be a number or an empty string",
  }).transform(val => val === '' ? '' : Number(val)),
]);

export const lineItemSchema = z.object({
  particulars: z.string().min(1, 'Particulars are required'),
  hsn: z.string().optional(),
  qty: numberOrEmptyString.optional(),
  rate: numberOrEmptyString.optional(),
  amount: numberOrEmptyString.optional(),
});

export const taxRowSchema = z.object({
  hsn: z.string().optional(),
  taxable: numberOrEmptyString.optional(),
  cgst_rate: numberOrEmptyString.optional(),
  cgst_amt: numberOrEmptyString.optional(),
  sgst_rate: numberOrEmptyString.optional(),
  sgst_amt: numberOrEmptyString.optional(),
});

export const invoiceSchema = z.object({
  seller: z.object({
    name: z.string().min(1, 'Seller name is required'),
    name_short: z.string().optional(),
    addr1: z.string().optional(),
    addr2: z.string().optional(),
    gstin: z.string().optional(),
    state_name: z.string().optional(),
    state_code: z.string().optional(),
    email: z.string().email().optional().or(emptyStringToUndefined),
    pan: z.string().optional(),
    logoUrl: z.string().url().optional().or(emptyStringToUndefined),
  }),
  buyer: z.object({
    name: z.string().min(1, 'Buyer name is required'),
    address: z.string().optional(),
    gstin: z.string().optional(),
    state_name: z.string().optional(),
    state_code: z.string().optional(),
  }),
  invoice: z.object({
    no: z.string().min(1, 'Invoice number is required'),
    date: z.string().min(1, 'Invoice date is required'),
    delivery_note: z.string().optional(),
    payment_terms: z.string().optional(),
    supplier_ref: z.string().optional(),
    other_ref: z.string().optional(),
    order_no: z.string().optional(),
    order_date: z.string().optional(),
    dispatch_doc: z.string().optional(),
    delivery_note_date: z.string().optional(),
    dispatch_through: z.string().optional(),
    destination: z.string().optional(),
    delivery_terms: z.string().optional(),
  }),
  items: z.array(lineItemSchema),
  totals: z.object({
    subtotal: numberOrEmptyString.optional(),
    taxable_total: numberOrEmptyString.optional(),
    cgst_total: numberOrEmptyString.optional(),
    sgst_total: numberOrEmptyString.optional(),
    tax_total: numberOrEmptyString.optional(),
    grand_total: numberOrEmptyString.optional(),
  }),
  tax_rows: z.array(taxRowSchema),
  amount_in_words: z.string().optional(),
  tax_amount_in_words: z.string().optional(),
  remarks: z.string().optional(),
  bank: z.object({
    name: z.string().optional(),
    acno: z.string().optional(),
    branch_ifsc: z.string().optional(),
    swift: z.string().optional(),
  }),
});

export type LineItem = z.infer<typeof lineItemSchema>;
export type TaxRow = z.infer<typeof taxRowSchema>;
export type InvoiceData = z.infer<typeof invoiceSchema>;

export const demoInvoiceData: InvoiceData = {
  seller: {
    name: "Tech Innovations Pvt. Ltd.",
    name_short: "Tech Innovations",
    addr1: "123, Silicon Avenue, Hitech City",
    addr2: "Hyderabad, Telangana, 500081",
    gstin: "36AAAAA0000A1Z5",
    state_name: "Telangana",
    state_code: "36",
    email: "contact@techinnovations.co.in",
    pan: "AAAAA0000A",
  },
  buyer: {
    name: "Creative Solutions LLP",
    address: "456, Bannerghatta Road, Bangalore, Karnataka, 560076",
    gstin: "29BBBBB1111B2Z6",
    state_name: "Karnataka",
    state_code: "29",
  },
  invoice: {
    no: "TI-2024-001",
    date: format(new Date(), 'dd-MMM-yy'),
    payment_terms: "Due upon receipt",
    delivery_terms: "F.O.R. Destination",
    order_no: "CS-PO-1024",
    order_date: format(new Date(new Date().setDate(new Date().getDate() - 5)), 'dd-MMM-yy'),
    dispatch_through: 'Express Courier',
    destination: 'Bangalore',
  },
  items: [
    { particulars: "Custom Software Development (Phase 1)", hsn: "998314", qty: 1, rate: 80000, amount: 80000 },
    { particulars: "Cloud Hosting & Setup (Annual)", hsn: "998315", qty: 1, rate: 15000, amount: 15000 },
    { particulars: "Technical Support Retainer (6 months)", hsn: "998319", qty: 6, rate: 2500, amount: 15000 },
  ],
  tax_rows: [
    { hsn: "998314", taxable: 80000, cgst_rate: 9, cgst_amt: 7200, sgst_rate: 9, sgst_amt: 7200 },
    { hsn: "998315", taxable: 15000, cgst_rate: 9, cgst_amt: 1350, sgst_rate: 9, sgst_amt: 1350 },
    { hsn: "998319", taxable: 15000, cgst_rate: 9, cgst_amt: 1350, sgst_rate: 9, sgst_amt: 1350 },
  ],
  totals: {
    subtotal: 110000,
    taxable_total: 110000,
    cgst_total: 9900,
    sgst_total: 9900,
    tax_total: 19800,
    grand_total: 129800,
  },
  amount_in_words: "One Lakh Twenty-Nine Thousand Eight Hundred Rupees Only",
  tax_amount_in_words: "Nineteen Thousand Eight Hundred Rupees Only",
  remarks: "This is a computer generated invoice and does not require a signature.",
  bank: {
    name: "Global Commercial Bank",
    acno: "01234567890",
    branch_ifsc: "GCBL0001234, Hitech City Branch",
  },
};
