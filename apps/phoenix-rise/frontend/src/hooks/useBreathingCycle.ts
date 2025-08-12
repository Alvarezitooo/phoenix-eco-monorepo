import { useReducer, useEffect, useRef } from 'react';

enum BreathingPhase {
  INSPIRE = 'inspire',
  HOLD = 'hold',
  EXPIRE = 'expire',
}

interface CycleState {
  phase: BreathingPhase;
  duration: number;
  remaining: number;
}

interface CycleAction {
  type: 'TICK' | 'RESET';
  nextPhase?: BreathingPhase;
}

const cycleConfig = {
  [BreathingPhase.INSPIRE]: { next: BreathingPhase.HOLD, duration: 4, label: 'Inspire' },
  [BreathingPhase.HOLD]: { next: BreathingPhase.EXPIRE, duration: 2, label: 'Garde' },
  [BreathingPhase.EXPIRE]: { next: BreathingPhase.INSPIRE, duration: 5, label: 'Expire' },
};

function cycleReducer(state: CycleState, action: CycleAction): CycleState {
  switch (action.type) {
    case 'TICK':
      if (state.remaining > 1) {
        return { ...state, remaining: state.remaining - 1 };
      } else {
        const nextPhaseConfig = cycleConfig[state.phase].next;
        const nextDuration = cycleConfig[nextPhaseConfig].duration;
        return {
          phase: nextPhaseConfig,
          duration: nextDuration,
          remaining: nextDuration,
        };
      }
    case 'RESET':
      const initialPhase = action.nextPhase || BreathingPhase.INSPIRE;
      const initialDuration = cycleConfig[initialPhase].duration;
      return {
        phase: initialPhase,
        duration: initialDuration,
        remaining: initialDuration,
      };
    default:
      return state;
  }
}

export function useBreathingCycle() {
  const [state, dispatch] = useReducer(cycleReducer, {
    phase: BreathingPhase.INSPIRE,
    duration: cycleConfig[BreathingPhase.INSPIRE].duration,
    remaining: cycleConfig[BreathingPhase.INSPIRE].duration,
  });

  const animationFrameRef = useRef<number>();
  const lastTimeRef = useRef<DOMHighResTimeStamp>(0);
  const accumulatedTimeRef = useRef<number>(0);

  useEffect(() => {
    const animate = (time: DOMHighResTimeStamp) => {
      if (!lastTimeRef.current) {
        lastTimeRef.current = time;
      }

      const deltaTime = time - lastTimeRef.current;
      accumulatedTimeRef.current += deltaTime;

      if (accumulatedTimeRef.current >= 1000) {
        const ticks = Math.floor(accumulatedTimeRef.current / 1000);
        dispatch({ type: 'TICK' });
        accumulatedTimeRef.current -= ticks * 1000;
      }

      lastTimeRef.current = time;
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const resetCycle = (initialPhase?: BreathingPhase) => {
    dispatch({ type: 'RESET', nextPhase: initialPhase });
  };

  return { ...state, label: cycleConfig[state.phase].label, resetCycle };
}