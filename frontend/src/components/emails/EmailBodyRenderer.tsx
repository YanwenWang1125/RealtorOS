'use client';

import { useEffect, useState } from 'react';
import DOMPurify from 'dompurify';

interface EmailBodyRendererProps {
  body: string;
}

export function EmailBodyRenderer({ body }: EmailBodyRendererProps) {
  const [sanitizedHtml, setSanitizedHtml] = useState('');

  useEffect(() => {
    // Sanitize HTML to prevent XSS attacks
    const clean = DOMPurify.sanitize(body, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'div', 'span', 'blockquote', 'pre', 'code'
      ],
      ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'style']
    });
    setSanitizedHtml(clean);
  }, [body]);

  return (
    <div
      className="prose prose-sm max-w-none"
      dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
    />
  );
}

