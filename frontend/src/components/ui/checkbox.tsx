"use client"

import * as React from "react"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils/index"

interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  onCheckedChange?: (checked: boolean) => void
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, checked, onCheckedChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (onCheckedChange) {
        onCheckedChange(e.target.checked)
      }
    }

    const handleClick = (e: React.MouseEvent) => {
      e.stopPropagation();
      if (props.onClick) {
        props.onClick(e as any);
      }
    }

    return (
      <div 
        className="relative inline-flex items-center cursor-pointer"
        onClick={(e) => {
          e.stopPropagation();
          if (onCheckedChange) {
            onCheckedChange(!checked);
          }
        }}
      >
        <input
          type="checkbox"
          ref={ref}
          checked={checked}
          onChange={handleChange}
          onClick={handleClick}
          className="sr-only peer"
          {...props}
        />
        <div
          className={cn(
            "h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background transition-colors",
            "peer-focus-visible:outline-none peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2",
            "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
            "flex items-center justify-center",
            checked ? "bg-primary text-primary-foreground border-primary" : "bg-background",
            className
          )}
        >
          {checked && (
            <Check className="h-3 w-3 text-primary-foreground" />
          )}
        </div>
      </div>
    )
  }
)
Checkbox.displayName = "Checkbox"

export { Checkbox }

