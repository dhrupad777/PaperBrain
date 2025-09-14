'use client';

import { useFieldArray, type UseFormReturn } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { FormControl, FormField, FormItem, FormLabel } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { PlusCircle, Trash2 } from 'lucide-react';
import { type InvoiceData } from '@/lib/invoiceSchema';
import { cn } from '@/lib/utils';
import { useEffect } from 'react';

interface ItemsEditorProps {
  form: UseFormReturn<InvoiceData>;
}

export function ItemsEditor({ form }: ItemsEditorProps) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'items',
  });

  const { control, watch, setValue } = form;

  // Watch for changes in qty and rate to auto-calculate amount
  useEffect(() => {
    const subscription = watch((value, { name, type }) => {
      if (type === 'change' && name && (name.startsWith('items') && (name.endsWith('.qty') || name.endsWith('.rate')))) {
        const parts = name.split('.');
        const index = parseInt(parts[1], 10);
        
        const items = value.items;
        if (items && items[index]) {
            const qty = Number(items[index].qty || 0);
            const rate = Number(items[index].rate || 0);
            setValue(`items.${index}.amount`, qty * rate);
        }
      }
    });
    return () => subscription.unsubscribe();
  }, [watch, setValue]);

  return (
    <div className="space-y-4">
      <div className="hidden lg:grid lg:grid-cols-[1fr_100px_100px_100px_120px_40px] gap-2 items-center text-sm font-medium">
        <FormLabel>Particulars</FormLabel>
        <FormLabel>HSN</FormLabel>
        <FormLabel>Qty</FormLabel>
        <FormLabel>Rate</FormLabel>
        <FormLabel>Amount</FormLabel>
        <span></span>
      </div>

      {fields.map((field, index) => (
        <div key={field.id} className="space-y-3 p-3 border rounded-lg bg-background">
          {/* Mobile Layout */}
          <div className="lg:hidden space-y-3">
            <FormField
              control={control}
              name={`items.${index}.particulars`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Particulars</FormLabel>
                  <FormControl><Input placeholder="Item description" {...field} /></FormControl>
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-3">
              <FormField
                control={control}
                name={`items.${index}.hsn`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>HSN</FormLabel>
                    <FormControl><Input placeholder="HSN/SAC" {...field} /></FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={control}
                name={`items.${index}.qty`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Qty</FormLabel>
                    <FormControl><Input type="number" placeholder="0" {...field} /></FormControl>
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <FormField
                control={control}
                name={`items.${index}.rate`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rate</FormLabel>
                    <FormControl><Input type="number" placeholder="0.00" {...field} /></FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={control}
                name={`items.${index}.amount`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Amount</FormLabel>
                    <FormControl><Input type="number" readOnly placeholder="0.00" {...field} className="font-semibold bg-muted" /></FormControl>
                  </FormItem>
                )}
              />
            </div>
            {fields.length > 1 && (
              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => remove(index)}
                  className="text-destructive hover:text-destructive"
                  aria-label="Remove item"
                >
                  <Trash2 className="h-4 w-4 mr-2" /> Remove Item
                </Button>
              </div>
            )}
          </div>

          {/* Desktop Layout */}
          <div className="hidden lg:grid lg:grid-cols-[1fr_100px_100px_100px_120px_40px] gap-2 items-start">
            <FormField
              control={control}
              name={`items.${index}.particulars`}
              render={({ field }) => (
                <FormItem>
                  <FormControl><Input placeholder="Item description" {...field} /></FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={control}
              name={`items.${index}.hsn`}
              render={({ field }) => (
                <FormItem>
                  <FormControl><Input placeholder="HSN/SAC" {...field} /></FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={control}
              name={`items.${index}.qty`}
              render={({ field }) => (
                <FormItem>
                  <FormControl><Input type="number" placeholder="0" {...field} /></FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={control}
              name={`items.${index}.rate`}
              render={({ field }) => (
                <FormItem>
                  <FormControl><Input type="number" placeholder="0.00" {...field} /></FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={control}
              name={`items.${index}.amount`}
              render={({ field }) => (
                <FormItem>
                  <FormControl><Input type="number" readOnly placeholder="0.00" {...field} className="font-semibold bg-muted" /></FormControl>
                </FormItem>
              )}
            />
            <div className="flex items-end h-full">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => remove(index)}
                className={cn("text-destructive hover:text-destructive", fields.length <= 1 ? "hidden" : "")}
                aria-label="Remove item"
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
        onClick={() => append({ particulars: '', hsn: '', qty: 1, rate: '', amount: '' })}
        className="w-full sm:w-auto"
      >
        <PlusCircle className="mr-2 h-4 w-4" /> Add Item
      </Button>
    </div>
  );
}
