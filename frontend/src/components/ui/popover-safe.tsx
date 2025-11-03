'use client';

import * as React from 'react';
import * as PopoverPrimitive from '@radix-ui/react-popover';
import { cn } from '@/lib/utils';

const PopoverSafe = PopoverPrimitive.Root;
const PopoverTrigger = PopoverPrimitive.Trigger;

// ✅ 重点：强制 Portal + 非 modal 模式（避免和 Dialog 冲突）
const PopoverContent = React.forwardRef<
  React.ElementRef<typeof PopoverPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Content>
>(({ className, align = 'start', side = 'bottom', sideOffset = 4, ...props }, ref) => (
  <PopoverPrimitive.Portal>
    <PopoverPrimitive.Content
      ref={ref}
      align={align}
      side={side}
      sideOffset={sideOffset}
      forceMount                // ✅ 强制挂载，避免因状态同步问题不渲染
      avoidCollisions={false}   // ✅ 防止 Dialog 裁剪
      className={cn(
        'z-[9999] w-[var(--radix-popover-trigger-width)] rounded-md border bg-white p-0 shadow-md outline-none',
        className
      )}
      {...props}
    />
  </PopoverPrimitive.Portal>
));
PopoverContent.displayName = PopoverPrimitive.Content.displayName;

export { PopoverSafe, PopoverTrigger, PopoverContent };

