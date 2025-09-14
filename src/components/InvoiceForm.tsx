'use client';

import type { UseFormReturn } from 'react-hook-form';
import type { InvoiceData } from '@/lib/invoiceSchema';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Form, FormField, FormItem, FormLabel, FormMessage, FormControl } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { ItemsEditor } from './ItemsEditor';
import { TaxRowsEditor } from './TaxRowsEditor';
import { RefreshCw } from 'lucide-react';

interface InvoiceFormProps {
  form: UseFormReturn<InvoiceData>;
  recalculateTotals: () => void;
}

export function InvoiceForm({ form, recalculateTotals }: InvoiceFormProps) {
  return (
    <Form {...form}>
      <form className="space-y-8">
        <Accordion type="multiple" defaultValue={['seller', 'buyer', 'invoice', 'items']} className="w-full">
          <AccordionItem value="seller">
            <AccordionTrigger className="text-lg font-semibold">Seller Details</AccordionTrigger>
            <AccordionContent className="grid gap-4 md:grid-cols-2">
              <FormField name="seller.name" control={form.control} render={({ field }) => (
                <FormItem className="md:col-span-2">
                  <FormLabel>Name</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField name="seller.addr1" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Address Line 1</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="seller.addr2" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Address Line 2</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="seller.gstin" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>GSTIN</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="seller.pan" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>PAN</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="seller.state_name" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>State</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="seller.state_code" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>State Code</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="seller.email" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl><Input type="email" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField name="seller.logoUrl" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Logo URL</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
            </AccordionContent>
          </AccordionItem>
          
          <AccordionItem value="buyer">
            <AccordionTrigger className="text-lg font-semibold">Buyer Details</AccordionTrigger>
            <AccordionContent className="grid gap-4 md:grid-cols-2">
              <FormField name="buyer.name" control={form.control} render={({ field }) => (
                <FormItem className="md:col-span-2">
                  <FormLabel>Name</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField name="buyer.address" control={form.control} render={({ field }) => (
                <FormItem className="md:col-span-2">
                  <FormLabel>Address</FormLabel>
                  <FormControl><Textarea {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="buyer.gstin" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>GSTIN</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="buyer.state_name" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>State</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="buyer.state_code" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>State Code</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="invoice">
            <AccordionTrigger className="text-lg font-semibold">Invoice Meta</AccordionTrigger>
            <AccordionContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <FormField name="invoice.no" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Invoice No.</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField name="invoice.date" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Invoice Date</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
               <FormField name="invoice.payment_terms" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Payment Terms</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="invoice.order_no" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Order No.</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="invoice.order_date" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Order Date</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="invoice.dispatch_through" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Dispatch Through</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField name="invoice.destination" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Destination</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
               <FormField name="invoice.delivery_terms" control={form.control} render={({ field }) => (
                <FormItem className="sm:col-span-2 lg:col-span-2">
                  <FormLabel>Delivery Terms</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                </FormItem>
              )} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="items">
            <AccordionTrigger className="text-lg font-semibold">Line Items</AccordionTrigger>
            <AccordionContent>
              <ItemsEditor form={form} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="tax-rows">
            <AccordionTrigger className="text-lg font-semibold">Tax Rows</AccordionTrigger>
            <AccordionContent>
              <TaxRowsEditor form={form} />
            </AccordionContent>
          </AccordionItem>
          
          <div className="pt-6">
            <h3 className="text-lg font-semibold">Totals</h3>
            <div className="mt-4 grid grid-cols-2 gap-4 rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
                <FormField name="totals.subtotal" control={form.control} render={({ field }) => (
                    <FormItem>
                    <FormLabel>Subtotal</FormLabel>
                    <FormControl><Input type="number" readOnly {...field} className="font-semibold" /></FormControl>
                    </FormItem>
                )} />
                <FormField name="totals.tax_total" control={form.control} render={({ field }) => (
                    <FormItem>
                    <FormLabel>Tax Total</FormLabel>
                    <FormControl><Input type="number" readOnly {...field} className="font-semibold" /></FormControl>
                    </FormItem>
                )} />
                <FormField name="totals.grand_total" control={form.control} render={({ field }) => (
                    <FormItem className="col-span-2">
                    <FormLabel>Grand Total</FormLabel>
                    <FormControl><Input type="number" readOnly {...field} className="text-xl font-bold" /></FormControl>
                    </FormItem>
                )} />
                <div className="col-span-2">
                    <Button type="button" variant="outline" onClick={recalculateTotals}>
                        <RefreshCw className="mr-2 h-4 w-4" /> Recalculate Totals
                    </Button>
                </div>
            </div>
          </div>
          
          <AccordionItem value="remarks-bank">
            <AccordionTrigger className="text-lg font-semibold">Remarks & Bank</AccordionTrigger>
            <AccordionContent className="grid gap-6">
              <FormField name="remarks" control={form.control} render={({ field }) => (
                <FormItem>
                  <FormLabel>Remarks</FormLabel>
                  <FormControl><Textarea {...field} /></FormControl>
                </FormItem>
              )} />
              <div className="grid gap-4 md:grid-cols-2">
                <FormField name="bank.name" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Bank Name</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                  </FormItem>
                )} />
                <FormField name="bank.acno" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>A/C No.</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                  </FormItem>
                )} />
                <FormField name="bank.branch_ifsc" control={form.control} render={({ field }) => (
                  <FormItem className="md:col-span-2">
                    <FormLabel>Branch & IFSC</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                  </FormItem>
                )} />
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </form>
    </Form>
  );
}
