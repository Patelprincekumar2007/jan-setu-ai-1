import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layers } from 'lucide-react';
import styles from './Header.module.css';

export const Header: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Overview' },
    { path: '/submit', label: 'Submit Request' },
    { path: '/track', label: 'Track Status' },
    { path: '/dashboard', label: 'Officer Dashboard' },
    { path: '/datasets', label: 'Open Datasets' },
  ];

  return (
    <header className={styles.header}>
      <div className={styles.topBar}>
        <span>Digital Public Infrastructure Prototype &bull; Track 1: AI for Governance</span>
        <span className={styles.prototypeBadge}>Research &amp; Prototype Stage</span>
      </div>
      <div className={styles.container}>
        <Link to="/" className={styles.brand} aria-label="NagrikLens AI Home">
          <div className={styles.brandIcon}>
            <Layers size={18} strokeWidth={2.2} />
          </div>
          <div className={styles.brandText}>
            <span className={styles.brandTitle}>NagrikLens AI</span>
            <span className={styles.brandSubtitle}>Citizen Needs. Public Data. Better Decisions.</span>
          </div>
        </Link>
        <nav className={styles.nav} aria-label="Main Navigation">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`${styles.navLink} ${isActive ? styles.navLinkActive : ''}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
