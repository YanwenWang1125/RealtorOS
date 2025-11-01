'use client';

import React from 'react';

interface EditClientPageProps {
  params: {
    id: string;
  };
}

export default function EditClientPage({ params }: EditClientPageProps) {
  return (
    <div>
      <h1 className="text-2xl font-bold">Edit Client</h1>
      <p className="text-muted-foreground">Client ID: {params.id}</p>
      {/* Edit client form will be implemented here */}
    </div>
  );
}

