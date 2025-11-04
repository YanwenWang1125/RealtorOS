'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import Link from 'next/link';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  link?: string;
  description?: string;
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  color = 'text-primary',
  link,
  description
}: StatsCardProps) {
  const CardWrapper = link ? Link : 'div';

  return (
    <CardWrapper href={link || '#'} className={link ? 'block' : ''}>
      <Card className={cn(
        'hover:shadow-md transition-shadow',
        link && 'cursor-pointer hover:border-primary'
      )}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <Icon className={cn('h-5 w-5', color)} />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{value}</div>
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
        </CardContent>
      </Card>
    </CardWrapper>
  );
}

