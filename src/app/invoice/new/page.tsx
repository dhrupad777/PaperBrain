'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { invoiceSchema, demoInvoiceData, type InvoiceData } from '@/lib/invoiceSchema';
import { getAmountInWords } from '@/lib/words';
import { useToast } from '@/hooks/use-toast';
import { InvoiceForm } from '@/components/InvoiceForm';
import { InvoicePreview } from '@/components/InvoicePreview';
import { Toolbar } from '@/components/Toolbar';
import { Button } from '@/components/ui/button';
import { Eye, EyeOff } from 'lucide-react';

const SAVE_KEY = 'pb.invoice.draft';

export default function InvoiceBuilderPage() {
  const [isClient, setIsClient] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const { toast } = useToast();

  const form = useForm<InvoiceData>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: demoInvoiceData,
  });

  const { control, reset, getValues, setValue, formState, trigger } = form;
  const watchedData = useWatch({ control });

  // Load from localStorage on mount
  useEffect(() => {
    setIsClient(true);
    const savedData = localStorage.getItem(SAVE_KEY);
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData);
        reset(parsedData);
        toast({ title: "Draft Loaded", description: "Your previously saved draft has been loaded." });
      } catch (error) {
        console.error("Failed to parse saved invoice data", error);
        localStorage.removeItem(SAVE_KEY);
      }
    }
  }, [reset, toast]);

  // Autosave to localStorage
  useEffect(() => {
    const subscription = form.watch((value) => {
      localStorage.setItem(SAVE_KEY, JSON.stringify(value));
    });
    return () => subscription.unsubscribe();
  }, [form]);


  const recalculateTotals = useCallback(() => {
    const items = getValues('items') || [];
    const tax_rows = getValues('tax_rows') || [];

    const subtotal = items.reduce((acc, item) => acc + Number(item.amount || 0), 0);
    const taxableTotal = tax_rows.reduce((acc, row) => acc + Number(row.taxable || 0), 0);
    const cgstTotal = tax_rows.reduce((acc, row) => acc + Number(row.cgst_amt || 0), 0);
    const sgstTotal = tax_rows.reduce((acc, row) => acc + Number(row.sgst_amt || 0), 0);
    const taxTotal = cgstTotal + sgstTotal;
    const grandTotal = subtotal + taxTotal;
    
    setValue('totals.subtotal', subtotal);
    setValue('totals.taxable_total', taxableTotal);
    setValue('totals.cgst_total', cgstTotal);
    setValue('totals.sgst_total', sgstTotal);
    setValue('totals.tax_total', taxTotal);
    setValue('totals.grand_total', grandTotal);

    Promise.all([
      getAmountInWords(grandTotal),
      getAmountInWords(taxTotal)
    ]).then(([amountInWords, taxAmountInWords]) => {
      setValue('amount_in_words', amountInWords);
      setValue('tax_amount_in_words', taxAmountInWords);
    });

  }, [getValues, setValue]);

  useEffect(() => {
    const subscription = form.watch((value, { name }) => {
      if (name?.startsWith('items') || name?.startsWith('tax_rows')) {
        recalculateTotals();
      }
    });
    return () => subscription.unsubscribe();
  }, [form, recalculateTotals]);


  const handleReset = () => {
    if (window.confirm("Are you sure you want to reset to the demo data? All your changes will be lost.")) {
      reset(demoInvoiceData);
      toast({ title: "Form Reset", description: "The form has been reset to the demo data." });
    }
  };

  if (!isClient) {
    return null; // or a loading skeleton
  }

  return (
    <div className="flex h-screen flex-col bg-muted/40 no-print">
      <Toolbar onReset={handleReset} invoiceData={watchedData} form={form} showPreview={showPreview} setShowPreview={setShowPreview} />
      <main className="flex-1 overflow-hidden pt-16">
        <div className="flex h-full flex-col lg:grid lg:grid-cols-2">
          <div className="h-full overflow-y-auto p-4 md:p-6 lg:p-8">
            <InvoiceForm form={form} recalculateTotals={recalculateTotals} />
          </div>
          <div className={`h-full flex-col items-center justify-center overflow-y-auto bg-gray-200 p-4 md:p-8 lg:flex ${showPreview ? 'flex' : 'hidden lg:flex'}`}>
            <div className="w-full max-w-2xl mx-auto">
              <div className="scale-[0.7] sm:scale-[0.8] lg:scale-90 origin-top">
                <InvoicePreview data={watchedData} />
              </div>
            </div>
          </div>
        </div>
        
        {/* Mobile Preview Toggle FAB */}
        <div className="fixed bottom-4 right-4 z-50 lg:hidden">
          <Button
            size="lg"
            onClick={() => setShowPreview(!showPreview)}
            className="rounded-full shadow-lg"
          >
            {showPreview ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </Button>
        </div>
      </main>
    </div>
  );
}
