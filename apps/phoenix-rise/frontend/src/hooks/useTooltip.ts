import { useState, useCallback } from 'react';

interface TooltipState {
  content: string;
  x: number;
  y: number;
  isVisible: boolean;
}

export function useTooltip() {
  const [tooltipState, setTooltipState] = useState<TooltipState>({
    content: '',
    x: 0,
    y: 0,
    isVisible: false,
  });

  const showTooltip = useCallback((content: string, x: number, y: number) => {
    setTooltipState({
      content,
      x,
      y,
      isVisible: true,
    });
  }, []);

  const hideTooltip = useCallback(() => {
    setTooltipState((prevState) => ({ ...prevState, isVisible: false }));
  }, []);

  return { tooltipState, showTooltip, hideTooltip };
}