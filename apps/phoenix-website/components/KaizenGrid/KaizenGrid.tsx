import React from 'react';
import { FixedSizeGrid } from 'react-window';
import { useKaizenHistory } from './useKaizenHistory';
import KaizenCell from './KaizenCell';
import Tooltip from './Tooltip';
import { useTooltip } from './useTooltip';

// Define column and row counts for a typical year (e.g., 52 weeks * 7 days)
const COLUMN_COUNT = 7; // Days of the week
const ROW_HEIGHT = 30; // Height of each cell
const COLUMN_WIDTH = 30; // Width of each cell

interface KaizenGridProps {
  userId: string;
}

export default function KaizenGrid({ userId }: KaizenGridProps) {
  const { data, loading, error, toggleKaizenStatus } = useKaizenHistory(userId);
  const { tooltipState, showTooltip, hideTooltip } = useTooltip();

  if (loading) {
    return <div className="kaizen-grid-status">Chargement de l'historique Kaizen...</div>;
  }

  if (error) {
    return <div className="kaizen-grid-status error">Erreur: {error}</div>;
  }

  // CellRenderer for react-window
  const Cell = ({ columnIndex, rowIndex, style }) => {
    const index = rowIndex * COLUMN_COUNT + columnIndex;
    const item = data[index];

    if (!item) return null; // Handle cases where index is out of bounds for data

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const content = item.completed ? `Kaizen accompli le ${item.date}` : `Aucun Kaizen le ${item.date}`;
      showTooltip(content, rect.left + rect.width / 2, rect.top - 10); // Position above cell
    };

    const handleClick = () => {
      toggleKaizenStatus(item.date);
    };

    return (
      <div style={style}>
        <KaizenCell
          date={item.date}
          isDone={item.completed}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={hideTooltip}
          onClick={handleClick}
        />
      </div>
    );
  };

  const rowCount = Math.ceil(data.length / COLUMN_COUNT);

  return (
    <>
      <FixedSizeGrid
        columnCount={COLUMN_COUNT}
        columnWidth={COLUMN_WIDTH}
        height={ROW_HEIGHT * Math.min(rowCount, 10)} // Display max 10 rows initially, scroll for more
        rowCount={rowCount}
        rowHeight={ROW_HEIGHT}
        width={COLUMN_WIDTH * COLUMN_COUNT} // Adjust grid width based on column count
        className="kaizen-grid-virtualized"
      >
        {Cell}
      </FixedSizeGrid>
      <Tooltip
        content={tooltipState.content}
        x={tooltipState.x}
        y={tooltipState.y}
        isVisible={tooltipState.isVisible}
      />
    </>
  );
}