import React, { forwardRef, useImperativeHandle, useCallback } from 'react';
import { FixedSizeGrid } from 'react-window';
import { useKaizenHistory } from '../hooks/useKaizenHistory';
import KaizenCell from './KaizenCell';
import Tooltip from './Tooltip';
import { useTooltip } from '../hooks/useTooltip';

const COLUMN_COUNT = 7;
const ROW_HEIGHT = 30;
const COLUMN_WIDTH = 30;

interface KaizenGridProps {
  userId: string;
}

interface KaizenGridRef {
  refreshKaizenHistory: () => void;
}

const KaizenGrid = forwardRef<KaizenGridRef, KaizenGridProps>(({ userId }, ref) => {
  const { data, loading, error, toggleKaizenStatus, refreshKaizenHistory } =
    useKaizenHistory(userId);
  const { tooltipState, showTooltip, hideTooltip } = useTooltip();

  useImperativeHandle(ref, () => ({
    refreshKaizenHistory,
  }));

  const Cell = useCallback(
    ({
      columnIndex,
      rowIndex,
      style,
    }: {
      columnIndex: number;
      rowIndex: number;
      style: React.CSSProperties;
    }) => {
      const index = rowIndex * COLUMN_COUNT + columnIndex;
      const item = data[index];

      if (!item) return null;

      const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const content = item.completed
          ? `Kaizen accompli le ${item.date}`
          : `Aucun Kaizen le ${item.date}`;
        showTooltip(content, rect.left + rect.width / 2, rect.top - 10);
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
    },
    [data, showTooltip, hideTooltip, toggleKaizenStatus],
  );

  const rowCount = Math.ceil(data.length / COLUMN_COUNT);

  return (
    <>
      {loading && <div className="kaizen-grid-status">Chargement de l'historique Kaizen...</div>}
      {!loading && error && <div className="kaizen-grid-status error">Erreur: {error}</div>}
      {!loading && !error && (
        <FixedSizeGrid
          columnCount={COLUMN_COUNT}
          columnWidth={COLUMN_WIDTH}
          height={ROW_HEIGHT * Math.min(rowCount, 10)}
          rowCount={rowCount}
          rowHeight={ROW_HEIGHT}
          width={COLUMN_WIDTH * COLUMN_COUNT}
          className="kaizen-grid-virtualized"
        >
          {Cell}
        </FixedSizeGrid>
      )}
      <Tooltip
        content={tooltipState.content}
        x={tooltipState.x}
        y={tooltipState.y}
        isVisible={tooltipState.isVisible}
      />
    </>
  );
});

KaizenGrid.displayName = 'KaizenGrid';

export default KaizenGrid;