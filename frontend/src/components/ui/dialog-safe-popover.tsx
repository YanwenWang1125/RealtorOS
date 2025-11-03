'use client';

import * as React from 'react';
import * as PopoverPrimitive from '@radix-ui/react-popover';
import { cn } from '@/lib/utils';

// ✅ 这是 Dialog 内部使用的安全版 Popover
const DialogSafePopover = PopoverPrimitive.Root;
const DialogSafeTrigger = PopoverPrimitive.Trigger;

const DialogSafeContent = React.forwardRef<
  React.ElementRef<typeof PopoverPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Content>
>(({ className, align = 'start', side = 'bottom', sideOffset = 4, ...props }, ref) => (
  <PopoverPrimitive.Portal>
    <PopoverPrimitive.Content
      ref={ref}
      align={align}
      side={side}
      sideOffset={sideOffset}
      // ✅ 关键属性：强制挂载，避免 Dialog 裁剪
      forceMount
      avoidCollisions={false}
      // ✅ 确保能被点击
      style={{ pointerEvents: 'auto' }}
      className={cn(
        'z-[9999] w-[var(--radix-popover-trigger-width)] rounded-md border bg-white p-0 shadow-md outline-none',
        className
      )}
      {...props}
    />
  </PopoverPrimitive.Portal>
));

DialogSafeContent.displayName = 'DialogSafeContent';

export { DialogSafePopover, DialogSafeTrigger, DialogSafeContent };

