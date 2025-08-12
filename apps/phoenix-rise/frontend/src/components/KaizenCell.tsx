import React from 'react';

interface KaizenCellProps {
  date: string;
  isDone: boolean;
  onMouseEnter: (event: React.MouseEvent<HTMLDivElement>) => void;
  onMouseLeave: (event: React.MouseEvent<HTMLDivElement>) => void;
  onClick: () => void;
}

export default function KaizenCell({
  date,
  isDone,
  onMouseEnter,
  onMouseLeave,
  onClick,
}: KaizenCellProps) {
  return (
    <div
      className={`kaizen-cell ${isDone ? 'done' : 'missed'}`}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
    ></div>
  );
}