import React from 'react';
import { AlertCircle } from 'lucide-react';
import { PageContainer } from '../components/common/PageContainer';
import styles from './LegalPages.module.css';

export const TermsPage: React.FC = () => {
  return (
    <PageContainer
      title="Terms and Conditions of Public Service Use"
      subtitle="Operational boundaries and terms of interaction with the NagrikLens AI prototype."
    >
      <div className={styles.legalContainer}>
        <div className={styles.prototypeBanner}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Prototype Notice:</strong> These terms are provided for hackathon demonstration purposes. This service is not an official government portal and does not provide legally binding guarantees of administrative action.
            </div>
          </div>
        </div>

        <div className={styles.section}>
          <h2>1. Scope of Service</h2>
          <p>
            NagrikLens AI is an experimental decision-support interface created to demonstrate how AI and open public datasets can assist civic infrastructure planning. It does not replace official state grievance portals or statutory emergency response lines.
          </p>
        </div>

        <div className={styles.section}>
          <h2>2. No Autonomous Government Authority</h2>
          <p>
            The system generates recommendations, priority scores, and project briefs for review by human policymakers. NagrikLens AI does not make autonomous fiscal allocations, issue tenders, or execute public works.
          </p>
        </div>

        <div className={styles.section}>
          <h2>3. Acceptable Use</h2>
          <p>
            Users agree not to submit fraudulent reports, defamatory content, or automated spam. The platform is intended solely for civic development and community welfare reporting.
          </p>
        </div>

        <div className={styles.section}>
          <h2>4. Limitation of Liability</h2>
          <p>
            The developers and hackathon contributors assume no liability for delays, unaddressed submissions, or inaccuracies in public baseline indicators during the demonstration period.
          </p>
        </div>
      </div>
    </PageContainer>
  );
};
