import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Footer.module.css';

export const Footer: React.FC = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.disclaimerBox}>
          <strong>Prototype Notice:</strong> NagrikLens AI is an architectural prototype developed for the Build with AI Hackathon (Track 1: Digital Public Infrastructure &amp; Governance). It serves as an evidence-based decision-support aid and does not replace statutory administrative procedures or official grievance redressal channels.
        </div>

        <div className={styles.grid}>
          <div className={styles.col}>
            <h4>NagrikLens AI</h4>
            <p className={styles.description}>
              Bridging the gap between multilingual citizen development requests, baseline census indicators, and government scheme allocations through structured AI workflows.
            </p>
          </div>
          <div className={styles.col}>
            <h4>Platform Navigation</h4>
            <ul className={styles.list}>
              <li><Link to="/">Architecture Overview</Link></li>
              <li><Link to="/submit">Citizen Request Portal</Link></li>
              <li><Link to="/track">Application Status Tracker</Link></li>
              <li><Link to="/dashboard">Officer Decision Dashboard</Link></li>
              <li><Link to="/datasets">Open Datasets Catalog</Link></li>
            </ul>
          </div>
          <div className={styles.col}>
            <h4>Governance &amp; Trust</h4>
            <ul className={styles.list}>
              <li><Link to="/privacy-policy">Civic Data Privacy Policy</Link></li>
              <li><Link to="/terms">Terms of Prototype Use</Link></li>
              <li><a href="https://github.com" target="_blank" rel="noopener noreferrer">Source Repository</a></li>
            </ul>
          </div>
        </div>

        <div className={styles.bottomBar}>
          <span>NagrikLens AI &bull; Open Governance Technology Architecture</span>
          <span>Phase 1: Foundation Baseline</span>
        </div>
      </div>
    </footer>
  );
};
