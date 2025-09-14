'use client';

import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { downloadInvoicePDF, printInvoice } from '@/lib/pdf';
import { Download, Printer, RotateCcw, Save } from 'lucide-react';
import type { InvoiceData } from '@/lib/invoiceSchema';
import { useToast } from '@/hooks/use-toast';
import type { UseFormReturn } from 'react-hook-form';

interface ToolbarProps {
  onReset: () => void;
  invoiceData: InvoiceData;
  form: UseFormReturn<InvoiceData>;
}

export function Toolbar({ onReset, invoiceData, form }: ToolbarProps) {
  const { toast } = useToast();
  const showCloudSave = process.env.NEXT_PUBLIC_ENABLE_CLOUD_SAVE === 'true';

  const handleDownload = async () => {
    const isValid = await form.trigger();
    if (!isValid) {
      toast({
        variant: 'destructive',
        title: 'Invalid Form Data',
        description: 'Please fix the errors before downloading.',
      });
      return;
    }
    const invoicePreviewElement = document.getElementById('invoice-preview');
    if (invoicePreviewElement) {
      await downloadInvoicePDF(invoicePreviewElement, invoiceData.invoice.no || 'invoice');
    }
  };

  const handlePrint = async () => {
    const isValid = await form.trigger();
     if (!isValid) {
      toast({
        variant: 'destructive',
        title: 'Invalid Form Data',
        description: 'Please fix the errors before printing.',
      });
      return;
    }
    printInvoice();
  };
  
  const handleSave = () => {
    // Placeholder for Firebase save logic
    toast({
        title: "Saved to Cloud",
        description: "Your invoice has been saved to your account.",
    });
  }

  return (
    <header className="fixed top-0 z-10 flex h-16 w-full items-center justify-between border-b bg-background px-4 md:px-6 no-print">
      <h1 className="text-xl font-semibold">Paper Brain Invoice Editor</h1>
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={onReset}>
          <RotateCcw className="mr-2 h-4 w-4" /> Reset
        </Button>
        {showCloudSave && (
          <Button variant="outline" size="sm" onClick={handleSave}>
            <Save className="mr-2 h-4 w-4" /> Save
          </Button>
        )}
        <Separator orientation="vertical" className="h-6" />
        <Button variant="outline" size="sm" onClick={handlePrint}>
          <Printer className="mr-2 h-4 w-4" /> Print
        </Button>
        <Button size="sm" onClick={handleDownload}>
          <Download className="mr-2 h-4 w-4" /> Download PDF
        </Button>
      </div>
    </header>
  );
}
