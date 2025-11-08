/**
 * Formatting utility functions.
 */

import { format as formatDate, formatDistanceToNow, parseISO } from 'date-fns';

/**
 * Format a date string to a readable format.
 */
export function formatDateString(dateString: string | null | undefined): string {
  if (!dateString) return 'N/A';
  try {
    const date = parseISO(dateString);
    return formatDate(date, 'MMM dd, yyyy');
  } catch {
    return 'Invalid Date';
  }
}

/**
 * Format a date string or Date object with time.
 */
export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDate(dateObj, 'MMM dd, yyyy HH:mm');
  } catch {
    return 'Invalid Date';
  }
}

/**
 * Get relative time (e.g., "2 hours ago").
 */
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true });
  } catch {
    return 'Invalid Date';
  }
}

/**
 * Format a number as currency.
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

/**
 * Format a phone number.
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return 'N/A';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  return phone;
}

