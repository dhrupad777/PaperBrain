import type { InvoiceData } from '@/lib/invoiceSchema';
import { fmt, pct } from '@/lib/currency';
import Image from 'next/image';

interface InvoicePreviewProps {
  data: InvoiceData;
}

export function InvoicePreview({ data }: InvoicePreviewProps) {
  const { seller, buyer, invoice, items, totals, tax_rows, amount_in_words, tax_amount_in_words, remarks, bank } = data;
  const grandTotal = Number(totals?.grand_total || 0);

  return (
    <>
      <style jsx global>{`
        .invoice-page {
          width: 210mm;
          min-height: 297mm;
          font-family: 'Inter', sans-serif;
          page-break-after: always;
        }
        @media print {
          body { background: white !important; }
          .invoice-page {
            margin: 0;
            padding: 0;
            border: none;
            box-shadow: none;
            transform: scale(1);
          }
        }
        @media (max-width: 768px) {
          .invoice-page {
            width: 100%;
            min-height: auto;
            font-size: 8pt;
            padding: 8px;
          }
        }
      `}</style>
      <div id="invoice-preview" className="invoice-page bg-white text-gray-800 shadow-lg p-[10mm] border border-gray-300 text-[9pt] leading-normal overflow-x-auto">
        <header className="flex flex-col sm:flex-row items-start justify-between pb-2 border-b-2 border-gray-800 gap-4">
          <div className="w-full sm:w-1/2">
            {seller.logoUrl ? (
                <Image src={seller.logoUrl} alt="Seller Logo" width={120} height={60} className="object-contain"/>
            ) : (
                <div className="w-32 h-16 border-2 border-dashed flex items-center justify-center text-gray-400">
                    LOGO
                </div>
            )}
            <h2 data-field="seller.name" className="font-bold text-lg mt-2">{seller.name}</h2>
            <p data-field="seller.addr1">{seller.addr1}</p>
            <p data-field="seller.addr2">{seller.addr2}</p>
          </div>
          <div className="w-full sm:w-1/2 sm:text-right">
            <h1 className="font-bold text-2xl sm:text-3xl text-gray-800">TAX INVOICE</h1>
            <table className="w-full mt-2">
              <tbody>
                <tr>
                  <td className="font-bold text-left pr-2">Invoice No:</td>
                  <td data-field="invoice.no" className="font-mono">{invoice.no}</td>
                </tr>
                <tr>
                  <td className="font-bold text-left pr-2">Invoice Date:</td>
                  <td data-field="invoice.date" className="font-mono">{invoice.date}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </header>

        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-2 border-b border-gray-300">
          <div>
            <h3 className="font-bold">SELLER:</h3>
            <p>GSTIN: <span data-field="seller.gstin" className="font-mono">{seller.gstin}</span></p>
            <p>PAN: <span data-field="seller.pan" className="font-mono">{seller.pan}</span></p>
            <p>State: <span data-field="seller.state_name">{seller.state_name}</span> (Code: <span data-field="seller.state_code">{seller.state_code}</span>)</p>
            <p>E-Mail: <span data-field="seller.email">{seller.email}</span></p>
          </div>
          <div>
            <h3 className="font-bold">BUYER (BILL TO):</h3>
            <p data-field="buyer.name" className="font-bold">{buyer.name}</p>
            <p data-field="buyer.address" className="whitespace-pre-line">{buyer.address}</p>
            <p>GSTIN: <span data-field="buyer.gstin" className="font-mono">{buyer.gstin}</span></p>
            <p>State: <span data-field="buyer.state_name">{buyer.state_name}</span> (Code: <span data-field="buyer.state_code">{buyer.state_code}</span>)</p>
          </div>
        </section>

        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-2 border-b border-gray-300">
          <div>
            <p>Order No: <span data-field="invoice.order_no" className="font-mono">{invoice.order_no}</span></p>
            <p>Order Date: <span data-field="invoice.order_date" className="font-mono">{invoice.order_date}</span></p>
            <p>Dispatch Through: <span data-field="invoice.dispatch_through">{invoice.dispatch_through}</span></p>
          </div>
           <div>
            <p>Destination: <span data-field="invoice.destination">{invoice.destination}</span></p>
            <p>Terms of Delivery: <span data-field="invoice.delivery_terms">{invoice.delivery_terms}</span></p>
            <p>Payment Terms: <span data-field="invoice.payment_terms">{invoice.payment_terms}</span></p>
          </div>
        </section>


        <section className="flex-grow py-2">
          <div className="overflow-x-auto">
            <table className="w-full text-left min-w-[600px]" cellPadding="2">
              <thead className="border-b-2 border-t-2 border-gray-800">
                <tr>
                  <th className="w-[5%]">S.No.</th>
                  <th className="w-[45%]">Particulars of Goods / Services</th>
                  <th className="w-[10%]">HSN/SAC</th>
                  <th className="w-[10%] text-right">Qty</th>
                  <th className="w-[15%] text-right">Rate</th>
                  <th className="w-[15%] text-right">Amount (INR)</th>
                </tr>
              </thead>
            <tbody id="items-body">
              {items?.map((item, index) => (
                <tr key={index} className="border-b border-gray-200 align-top">
                  <td>{index + 1}.</td>
                  <td className="py-1">{item.particulars}</td>
                  <td>{item.hsn}</td>
                  <td className="text-right">{item.qty}</td>
                  <td className="text-right">{fmt(item.rate)}</td>
                  <td className="text-right font-semibold">{fmt(item.amount)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-b-2 border-t-2 border-gray-800 font-bold">
                <td colSpan={5} className="text-right">Subtotal</td>
                <td data-field="totals.subtotal" className="text-right">{fmt(totals?.subtotal)}</td>
              </tr>
              <tr className="font-bold">
                <td colSpan={5} className="text-right">CGST</td>
                <td data-field="totals.cgst_total" className="text-right">{fmt(totals?.cgst_total)}</td>
              </tr>
              <tr className="font-bold">
                <td colSpan={5} className="text-right">SGST</td>
                <td data-field="totals.sgst_total" className="text-right">{fmt(totals?.sgst_total)}</td>
              </tr>
              <tr className="border-b-2 border-t-2 border-gray-800 font-bold text-lg">
                <td colSpan={5} className="text-right">GRAND TOTAL</td>
                <td className="text-right">{fmt(grandTotal)}</td>
              </tr>
            </tfoot>
            </table>
          </div>
        </section>

        <section className="py-2 space-y-2">
          <div>
            <span className="font-bold">Amount in Words: </span>
            <span data-field="amount_in_words">{amount_in_words}</span>
          </div>
          <div>
            <span className="font-bold">Tax in Words: </span>
            <span data-field="tax_amount_in_words">{tax_amount_in_words}</span>
          </div>
        </section>

        <section className="py-2 border-t border-gray-300">
          <h3 className="font-bold text-center">TAX SUMMARY</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left mt-1 min-w-[500px]" cellPadding="2">
            <thead className="border-b border-t border-gray-300">
              <tr>
                <th className="w-1/4">HSN/SAC</th>
                <th className="w-1/4 text-right">Taxable Value</th>
                <th className="w-1/4 text-center" colSpan={2}>CGST</th>
                <th className="w-1/4 text-center" colSpan={2}>SGST</th>
              </tr>
              <tr>
                <th></th>
                <th></th>
                <th className="text-center w-[12.5%]">Rate</th>
                <th className="text-right w-[12.5%]">Amount</th>
                <th className="text-center w-[12.5%]">Rate</th>
                <th className="text-right w-[12.5%]">Amount</th>
              </tr>
            </thead>
            <tbody id="tax-rows">
              {tax_rows?.map((row, index) => (
                <tr key={index} className="border-b border-gray-200">
                  <td>{row.hsn}</td>
                  <td className="text-right">{fmt(row.taxable)}</td>
                  <td className="text-center">{pct(row.cgst_rate)}</td>
                  <td className="text-right">{fmt(row.cgst_amt)}</td>
                  <td className="text-center">{pct(row.sgst_rate)}</td>
                  <td className="text-right">{fmt(row.sgst_amt)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t-2 border-gray-800 font-bold">
              <tr>
                <td>Total</td>
                <td data-field="totals.taxable_total" className="text-right">{fmt(totals?.taxable_total)}</td>
                <td></td>
                <td data-field="totals.cgst_total" className="text-right">{fmt(totals?.cgst_total)}</td>
                <td></td>
                <td data-field="totals.sgst_total" className="text-right">{fmt(totals?.sgst_total)}</td>
              </tr>
            </tfoot>
            </table>
          </div>
        </section>
        
        <footer className="mt-auto pt-4 text-xs absolute bottom-[10mm] w-[calc(210mm-20mm)]">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-t-2 border-gray-800 pt-2">
            <div>
              <p className="font-bold">Bank Details:</p>
              <p>Bank Name: <span data-field="bank.name">{bank?.name}</span></p>
              <p>A/C No: <span data-field="bank.acno">{bank?.acno}</span></p>
              <p>Branch & IFSC: <span data-field="bank.branch_ifsc">{bank?.branch_ifsc}</span></p>
              <p data-field="remarks" className="mt-2 italic">{remarks}</p>
            </div>
            <div className="text-left sm:text-right">
              <p className="font-bold">For {seller.name}</p>
              <div className="h-16"></div>
              <p>Authorised Signatory</p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
