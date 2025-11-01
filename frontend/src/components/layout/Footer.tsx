/**
 * Footer component for the application layout.
 */

import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="text-center text-sm text-gray-600">
          <p>&copy; {new Date().getFullYear()} RealtorOS. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

