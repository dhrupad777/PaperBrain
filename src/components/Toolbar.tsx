'use client';

import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { downloadInvoicePDF, printInvoice } from '@/lib/pdf';
import { Download, Printer, RotateCcw, Save, Eye, EyeOff } from 'lucide-react';
import type { InvoiceData } from '@/lib/invoiceSchema';
import { useToast } from '@/hooks/use-toast';
import type { UseFormReturn } from 'react-hook-form';

interface ToolbarProps {
  onReset: () => void;
  invoiceData: InvoiceData;
  form: UseFormReturn<InvoiceData>;
  showPreview?: boolean;
  setShowPreview?: (show: boolean) => void;
}

export function Toolbar({ onReset, invoiceData, form, showPreview, setShowPreview }: ToolbarProps) {
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
    <header className="fixed top-0 z-10 flex h-16 w-full items-center justify-between border-b bg-background px-2 sm:px-4 md:px-6 no-print">
      <h1 className="text-sm sm:text-lg md:text-xl font-semibold truncate">Paper Brain</h1>
      <div className="flex items-center gap-1 sm:gap-2">
        <Button variant="outline" size="sm" onClick={onReset} className="hidden sm:flex">
          <RotateCcw className="mr-1 sm:mr-2 h-4 w-4" /> 
          <span className="hidden sm:inline">Reset</span>
        </Button>
        <Button variant="outline" size="sm" onClick={onReset} className="sm:hidden">
          <RotateCcw className="h-4 w-4" />
        </Button>
        {showCloudSave && (
          <Button variant="outline" size="sm" onClick={handleSave} className="hidden sm:flex">
            <Save className="mr-1 sm:mr-2 h-4 w-4" /> 
            <span className="hidden sm:inline">Save</span>
          </Button>
        )}
        {showCloudSave && (
          <Button variant="outline" size="sm" onClick={handleSave} className="sm:hidden">
            <Save className="h-4 w-4" />
          </Button>
        )}
        <Separator orientation="vertical" className="h-6 hidden sm:block" />
        <Button variant="outline" size="sm" onClick={handlePrint} className="hidden sm:flex">
          <Printer className="mr-1 sm:mr-2 h-4 w-4" /> 
          <span className="hidden sm:inline">Print</span>
        </Button>
        <Button variant="outline" size="sm" onClick={handlePrint} className="sm:hidden">
          <Printer className="h-4 w-4" />
        </Button>
        <Button size="sm" onClick={handleDownload} className="hidden sm:flex">
          <Download className="mr-1 sm:mr-2 h-4 w-4" /> 
          <span className="hidden sm:inline">Download PDF</span>
        </Button>
        <Button size="sm" onClick={handleDownload} className="sm:hidden">
          <Download className="h-4 w-4" />
        </Button>
        {setShowPreview && (
          <>
            <Separator orientation="vertical" className="h-6 hidden sm:block" />
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setShowPreview(!showPreview)}
              className="hidden sm:flex"
            >
              {showPreview ? <EyeOff className="mr-1 sm:mr-2 h-4 w-4" /> : <Eye className="mr-1 sm:mr-2 h-4 w-4" />}
              <span className="hidden sm:inline">{showPreview ? 'Hide Preview' : 'Show Preview'}</span>
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setShowPreview(!showPreview)}
              className="sm:hidden"
            >
              {showPreview ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </>
        )}
      </div>
    </header>
  );
}
