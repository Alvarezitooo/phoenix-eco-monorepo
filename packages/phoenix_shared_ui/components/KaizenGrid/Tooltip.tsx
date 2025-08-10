import React from 'react';

interface TooltipProps {
  content: string;
  x: number;
  y: number;
  isVisible: boolean;
}

export default function Tooltip({ content, x, y, isVisible }: TooltipProps) {
  if (!isVisible || !content) return null;

  return (
    <div
      className="kaizen-global-tooltip"
      style={{
        position: 'absolute',
        left: x,
        top: y,
        pointerEvents: 'none', // Ensure tooltip doesn't block mouse events on cells
        zIndex: 1000, // Ensure tooltip is on top
      }}
      role="tooltip"
    >
      {content}
    </div>
  );
}
