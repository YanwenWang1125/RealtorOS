'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';

interface CustomInstructionsInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function CustomInstructionsInput({ value, onChange }: CustomInstructionsInputProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const examples = [
    "Mention the new construction in the area",
    "Keep it very brief, max 3 sentences",
    "Focus on investment potential",
    "Emphasize family-friendly features"
  ];

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4" />
          Custom AI Instructions (Optional)
        </Label>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4 mr-1" />
              Hide
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4 mr-1" />
              Show
            </>
          )}
        </Button>
      </div>

      {isExpanded && (
        <>
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="e.g., Mention the nearby park, keep it brief..."
            rows={3}
            maxLength={500}
          />
          <div className="flex justify-between text-xs">
            <div className="text-muted-foreground">
              {value.length}/500 characters
            </div>
          </div>

          {/* Examples */}
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Examples:</p>
            <div className="flex flex-wrap gap-2">
              {examples.map((example, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-xs h-auto py-1"
                  onClick={() => onChange(example)}
                >
                  {example}
                </Button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

