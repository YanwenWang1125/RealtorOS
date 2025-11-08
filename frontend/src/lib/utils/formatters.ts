export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Normalize client stage value to handle case/whitespace issues.
 * Converts stage values to lowercase and trims whitespace, then maps
 * common variations to the correct stage format.
 */
export function normalizeClientStage(stage: string): 'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost' {
  if (!stage) return 'lead'; // Default fallback
  
  const normalized = stage.trim().toLowerCase().replace(/\s+/g, ' '); // Normalize whitespace
  // Map common variations to correct stage values
  const stageMap: Record<string, 'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost'> = {
    'lead': 'lead',
    'negotiating': 'negotiating',
    'negotiation': 'negotiating',
    'under_contract': 'under_contract',
    'under contract': 'under_contract',
    'undercontract': 'under_contract',
    'closed': 'closed',
    'close': 'closed',
    'lost': 'lost',
    'lose': 'lost'
  };
  
  // Check exact match first
  if (stageMap[normalized]) {
    return stageMap[normalized];
  }
  
  // Check if it contains key phrases (for more flexible matching)
  if (normalized.includes('under') && normalized.includes('contract')) {
    return 'under_contract';
  }
  if (normalized.includes('negotiat')) {
    return 'negotiating';
  }
  if (normalized.includes('close') && !normalized.includes('under')) {
    return 'closed';
  }
  if (normalized.includes('lost') || normalized.includes('lose')) {
    return 'lost';
  }
  if (normalized.includes('lead')) {
    return 'lead';
  }
  
  // Final fallback - try to use as-is if it matches a valid stage
  const validStages: Array<'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost'> = 
    ['lead', 'negotiating', 'under_contract', 'closed', 'lost'];
  if (validStages.includes(normalized as any)) {
    return normalized as 'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost';
  }
  
  // Default fallback
  return 'lead';
}