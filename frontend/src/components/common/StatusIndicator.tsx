import React from 'react';
import styles from './StatusIndicator.module.css';

export type StatusVariant =
  | 'planned'
  | 'connected'
  | 'verified'
  | 'warning'
  | 'pending'
  | 'error'
  | 'critical'
  | 'success'
  | 'info';

interface StatusIndicatorProps {
  status: StatusVariant;
  label: string;
  showDot?: boolean;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  showDot = true,
}) => {
  return (
    <span className={`${styles.badge} ${styles[status]}`}>
      {showDot && <span className={styles.dot} />}
      {label}
    </span>
  );
};
