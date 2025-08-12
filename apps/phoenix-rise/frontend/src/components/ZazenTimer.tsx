import React from 'react';
import { useBreathingCycle } from '../hooks/useBreathingCycle';

export default function ZazenTimer() {
  const { phase, remaining, label } = useBreathingCycle();

  return (
    <div className="zazen-container">
      <div
        className={`zazen-circle ${phase}`}
        role="timer"
        aria-live="polite"
        aria-atomic="true"
        aria-label={`Phase de respiration: ${label}, ${remaining} secondes restantes`}
      />
      <p className="zazen-text">
        {label}
        <br /> {remaining} secondes
      </p>
    </div>
  );
}