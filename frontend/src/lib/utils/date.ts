import { format, parseISO, isValid } from 'date-fns';

/**
 * Format a date with a custom format string.
 * This is a flexible date formatter that accepts custom format patterns.
 * For standard formatting functions, use the functions from './format'.
 */
export function formatDate(date: string | Date, formatStr: string = 'PPP'): string {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return isValid(dateObj) ? format(dateObj, formatStr) : 'Invalid date';
  } catch {
    return 'Invalid date';
  }
}
