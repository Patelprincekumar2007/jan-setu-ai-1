import React from 'react';
import { Header } from './Header';
import { Footer } from './Footer';
import styles from './PageContainer.module.css';

interface PageContainerProps {
  title?: string;
  subtitle?: string;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
}

export const PageContainer: React.FC<PageContainerProps> = ({
  title,
  subtitle,
  headerAction,
  children,
}) => {
  return (
    <div className={styles.layout}>
      <Header />
      <main className={styles.main}>
        {(title || subtitle || headerAction) && (
          <div className={styles.headerArea}>
            <div className={styles.titleRow}>
              <div>
                {title && <h1 className={styles.title}>{title}</h1>}
                {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
              </div>
              {headerAction && <div>{headerAction}</div>}
            </div>
          </div>
        )}
        {children}
      </main>
      <Footer />
    </div>
  );
};
