'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Plus, X } from 'lucide-react';

interface CustomFieldsEditorProps {
  fields: Record<string, any>;
  onChange: (fields: Record<string, any>) => void;
  disabled?: boolean;
}

export function CustomFieldsEditor({ fields, onChange, disabled }: CustomFieldsEditorProps) {
  const [entries, setEntries] = useState<Array<{ key: string; value: any }>>(
    Object.entries(fields || {}).map(([key, value]) => ({ key, value: String(value) }))
  );

  const handleAdd = () => {
    setEntries([...entries, { key: '', value: '' }]);
  };

  const handleRemove = (index: number) => {
    const newEntries = entries.filter((_, i) => i !== index);
    setEntries(newEntries);
    
    const fieldsObject = Object.fromEntries(
      newEntries.filter(e => e.key.trim()).map(e => [e.key.trim(), e.value])
    );
    onChange(fieldsObject);
  };

  const handleChange = (index: number, field: 'key' | 'value', newValue: string) => {
    const newEntries = [...entries];
    newEntries[index][field] = newValue;
    setEntries(newEntries);

    // Convert to object and pass to parent
    const fieldsObject = Object.fromEntries(
      newEntries.filter(e => e.key.trim()).map(e => [e.key.trim(), e.value])
    );
    onChange(fieldsObject);
  };

  // Validate for duplicate keys
  const duplicateKeys = entries
    .map((e, i) => ({ key: e.key.trim(), index: i }))
    .filter(e => e.key)
    .reduce((acc, curr) => {
      if (!acc[curr.key]) acc[curr.key] = [];
      acc[curr.key].push(curr.index);
      return acc;
    }, {} as Record<string, number[]>);

  return (
    <div className="space-y-2">
      {entries.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No custom fields. Click 'Add Field' to create one.
        </p>
      ) : (
        entries.map((entry, index) => {
          const hasDuplicate = duplicateKeys[entry.key.trim()]?.length > 1;
          return (
            <div key={index} className="flex gap-2">
              <div className="flex-1">
                <Input
                  placeholder="Field name"
                  value={entry.key}
                  onChange={(e) => handleChange(index, 'key', e.target.value)}
                  disabled={disabled}
                  maxLength={50}
                  className={hasDuplicate ? 'border-red-500' : ''}
                />
                {hasDuplicate && (
                  <p className="text-xs text-red-500 mt-1">Duplicate key</p>
                )}
              </div>
              <div className="flex-1">
                <Input
                  placeholder="Value"
                  value={entry.value}
                  onChange={(e) => handleChange(index, 'value', e.target.value)}
                  disabled={disabled}
                  maxLength={200}
                />
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => handleRemove(index)}
                disabled={disabled}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          );
        })
      )}
      <Button
        type="button"
        variant="outline"
        onClick={handleAdd}
        disabled={disabled || entries.length >= 20}
      >
        <Plus className="h-4 w-4 mr-2" />
        Add Field
      </Button>
    </div>
  );
}

