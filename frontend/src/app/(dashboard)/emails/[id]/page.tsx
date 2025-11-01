'use client';

import React from 'react';

interface EmailDetailPageProps {
  params: {
    id: string;
  };
}

export default function EmailDetailPage({ params }: EmailDetailPageProps) {
  return (
    <div>
      <h1 className="text-2xl font-bold">Email Details</h1>
      <p className="text-muted-foreground">Email ID: {params.id}</p>
      {/* Email details will be implemented here */}
    </div>
  );
}

