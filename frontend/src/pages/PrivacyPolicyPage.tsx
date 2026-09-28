import React from 'react';
import { AlertCircle } from 'lucide-react';
import { PageContainer } from '../components/common/PageContainer';
import styles from './LegalPages.module.css';

export const PrivacyPolicyPage: React.FC = () => {
  return (
    <PageContainer
      title="Civic Data Privacy Policy"
      subtitle="Data governance and privacy principles applied to citizen development requests."
    >
      <div className={styles.legalContainer}>
        <div className={styles.prototypeBanner}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Prototype Notice:</strong> This document is an architectural demonstration of civic data handling policies for the Build with AI Hackathon prototype. It is not a formal statutory legal instrument and has not undergone formal legal review.
            </div>
          </div>
        </div>

        <div className={styles.section}>
          <h2>1. Data Minimisation Principle</h2>
          <p>
            NagrikLens AI is designed to process community infrastructure requirements and development needs. We strictly enforce data minimisation:
          </p>
          <ul>
            <li>No national identity numbers (such as Aadhaar) or sensitive biometric data are requested or stored.</li>
            <li>No financial or banking information is collected.</li>
            <li>Users are requested to describe public infrastructure issues without including private individual contact details.</li>
          </ul>
        </div>

        <div className={styles.section}>
          <h2>2. Synthetic De-Identification and AI Processing</h2>
          <p>
            When text narratives are ingested, automated filtering scans for accidentally submitted personal telephone numbers or individual names, replacing them with administrative placeholders prior to indexing or analytical presentation.
          </p>
        </div>

        <div className={styles.section}>
          <h2>3. Open Data Grounding</h2>
          <p>
            Demographic and baseline statistics used for request evaluation are derived exclusively from publicly published aggregate datasets (such as District Census indicators). No private consumer profiling or personal tracking data is utilised.
          </p>
        </div>

        <div className={styles.section}>
          <h2>4. Data Retention</h2>
          <p>
            In the prototype phase, submitted records are temporary demonstration artifacts and are periodically reset during development cycles.
          </p>
        </div>
      </div>
    </PageContainer>
  );
};
