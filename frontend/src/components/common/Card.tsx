import React from 'react';
import styles from './Card.module.css';

interface CardProps {
  title?: React.ReactNode;
  subtitle?: string;
  headerAction?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  bordered?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  headerAction,
  footer,
  children,
  className = '',
  bordered = false,
}) => {
  return (
    <div className={`${styles.card} ${bordered ? styles.bordered : ''} ${className}`}>
      {(title || subtitle || headerAction) && (
        <div className={styles.cardHeader}>
          <div>
            {title && <h3 className={styles.title}>{title}</h3>}
            {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      <div className={styles.cardBody}>{children}</div>
      {footer && <div className={styles.cardFooter}>{footer}</div>}
    </div>
  );
};
