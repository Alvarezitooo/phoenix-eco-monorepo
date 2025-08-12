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
        pointerEvents: 'none',
        zIndex: 1000,
      }}
      role="tooltip"
    >
      {content}
    </div>
  );
}