'use client';

import { useFieldArray, type UseFormReturn } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { FormControl, FormField, FormItem, FormLabel } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { PlusCircle, Trash2 } from 'lucide-react';
import { type InvoiceData } from '@/lib/invoiceSchema';
import { cn } from '@/lib/utils';
import { useEffect } from 'react';

interface TaxRowsEditorProps {
  form: UseFormReturn<InvoiceData>;
}

export function TaxRowsEditor({ form }: TaxRowsEditorProps) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'tax_rows',
  });
  
  const { control, watch, setValue } = form;

  useEffect(() => {
    const subscription = watch((value, { name, type }) => {
      if (type === 'change' && name && name.startsWith('tax_rows') && (name.endsWith('.taxable') || name.endsWith('.cgst_rate') || name.endsWith('.sgst_rate'))) {
        const parts = name.split('.');
        const index = parseInt(parts[1], 10);
        
        const taxRows = value.tax_rows;
        if (taxRows && taxRows[index]) {
            const taxable = Number(taxRows[index].taxable || 0);
            const cgstRate = Number(taxRows[index].cgst_rate || 0);
            const sgstRate = Number(taxRows[index].sgst_rate || 0);
            
            setValue(`tax_rows.${index}.cgst_amt`, (taxable * cgstRate) / 100);
            setValue(`tax_rows.${index}.sgst_amt`, (taxable * sgstRate) / 100);
        }
      }
    });
    return () => subscription.unsubscribe();
  }, [watch, setValue]);


  return (
    <div className="space-y-4">
      <div className="hidden lg:grid lg:grid-cols-[1fr_1fr_1fr_1fr_1fr_1fr_40px] gap-2 items-center text-sm font-medium">
        <FormLabel>HSN</FormLabel>
        <FormLabel>Taxable Value</FormLabel>
        <FormLabel>CGST Rate</FormLabel>
        <FormLabel>CGST Amt</FormLabel>
        <FormLabel>SGST Rate</FormLabel>
        <FormLabel>SGST Amt</FormLabel>
        <span></span>
      </div>

      {fields.map((field, index) => (
        <div key={field.id} className="space-y-3 p-3 border rounded-lg bg-background">
          {/* Mobile Layout */}
          <div className="lg:hidden space-y-3">
            <FormField control={control} name={`tax_rows.${index}.hsn`} render={({ field }) => (
              <FormItem>
                <FormLabel>HSN/SAC</FormLabel>
                <FormControl><Input placeholder="HSN/SAC" {...field} /></FormControl>
              </FormItem>
            )} />
            <FormField control={control} name={`tax_rows.${index}.taxable`} render={({ field }) => (
              <FormItem>
                <FormLabel>Taxable Value</FormLabel>
                <FormControl><Input type="number" placeholder="0.00" {...field} /></FormControl>
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-3">
              <FormField control={control} name={`tax_rows.${index}.cgst_rate`} render={({ field }) => (
                <FormItem>
                  <FormLabel>CGST %</FormLabel>
                  <FormControl><Input type="number" placeholder="%" {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField control={control} name={`tax_rows.${index}.cgst_amt`} render={({ field }) => (
                <FormItem>
                  <FormLabel>CGST Amt</FormLabel>
                  <FormControl><Input type="number" readOnly placeholder="0.00" {...field} className="font-semibold bg-muted"/></FormControl>
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <FormField control={control} name={`tax_rows.${index}.sgst_rate`} render={({ field }) => (
                <FormItem>
                  <FormLabel>SGST %</FormLabel>
                  <FormControl><Input type="number" placeholder="%" {...field} /></FormControl>
                </FormItem>
              )} />
              <FormField control={control} name={`tax_rows.${index}.sgst_amt`} render={({ field }) => (
                <FormItem>
                  <FormLabel>SGST Amt</FormLabel>
                  <FormControl><Input type="number" readOnly placeholder="0.00" {...field} className="font-semibold bg-muted"/></FormControl>
                </FormItem>
              )} />
            </div>
            <div className="flex justify-end">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => remove(index)}
                className="text-destructive hover:text-destructive"
                aria-label="Remove tax row"
              >
                <Trash2 className="h-4 w-4 mr-2" /> Remove Tax Row
              </Button>
            </div>
          </div>

          {/* Desktop Layout */}
          <div className="hidden lg:grid lg:grid-cols-[1fr_1fr_1fr_1fr_1fr_1fr_40px] gap-2 items-start">
            <FormField control={control} name={`tax_rows.${index}.hsn`} render={({ field }) => (
              <FormItem><FormControl><Input placeholder="HSN/SAC" {...field} /></FormControl></FormItem>
            )} />
            <FormField control={control} name={`tax_rows.${index}.taxable`} render={({ field }) => (
              <FormItem><FormControl><Input type="number" placeholder="0.00" {...field} /></FormControl></FormItem>
            )} />
            <FormField control={control} name={`tax_rows.${index}.cgst_rate`} render={({ field }) => (
              <FormItem><FormControl><Input type="number" placeholder="%" {...field} /></FormControl></FormItem>
            )} />
            <FormField control={control} name={`tax_rows.${index}.cgst_amt`} render={({ field }) => (
              <FormItem><FormControl><Input type="number" readOnly placeholder="0.00" {...field} className="font-semibold bg-muted"/></FormControl></FormItem>
            )} />
            <FormField control={control} name={`tax_rows.${index}.sgst_rate`} render={({ field }) => (
              <FormItem><FormControl><Input type="number" placeholder="%" {...field} /></FormControl></FormItem>
            )} />
            <FormField control={control} name={`tax_rows.${index}.sgst_amt`} render={({ field }) => (
              <FormItem><FormControl><Input type="number" readOnly placeholder="0.00" {...field} className="font-semibold bg-muted"/></FormControl></FormItem>
            )} />
            <div className="flex items-end h-full">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => remove(index)}
                className="text-destructive hover:text-destructive"
                aria-label="Remove tax row"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      ))}
      <Button
        type="button"
        variant="outline"
        onClick={() => append({ hsn: '', taxable: '', cgst_rate: 9, cgst_amt: '', sgst_rate: 9, sgst_amt: '' })}
        className="w-full sm:w-auto"
      >
        <PlusCircle className="mr-2 h-4 w-4" /> Add Tax Row
      </Button>
    </div>
  );
}
