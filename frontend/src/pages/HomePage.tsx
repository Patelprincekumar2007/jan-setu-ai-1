import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Search, BarChart3, ShieldCheck, Users, Building2 } from 'lucide-react';
import { PageContainer } from '../components/common/PageContainer';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import styles from './HomePage.module.css';

export const HomePage: React.FC = () => {
  return (
    <PageContainer>
      {/* Hero Section */}
      <section className={styles.hero}>
        <span className={styles.heroTag}>Digital Public Infrastructure Concept</span>
        <h1 className={styles.heroTitle}>
          Multilingual Citizen Development Intelligence Platform
        </h1>
        <p className={styles.heroDescription}>
          NagrikLens AI helps organize citizen development requests and connect them with public data to support evidence-based infrastructure prioritisation.
        </p>
        <div className={styles.heroActions}>
          <Link to="/submit">
            <Button variant="primary" size="lg" icon={<FileText size={16} />}>
              Submit Development Request
            </Button>
          </Link>
          <Link to="/track">
            <Button variant="outline" size="lg" icon={<Search size={16} />}>
              Track Reference ID
            </Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="secondary" size="lg" icon={<BarChart3 size={16} />}>
              Officer Dashboard
            </Button>
          </Link>
        </div>
      </section>

      {/* Core Objectives (WHAT & WHO) */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Platform Scope &amp; Target Stakeholders</h2>
          <p className={styles.sectionSubtitle}>
            Bridging fragmented citizen inputs with ground-truth public datasets.
          </p>
        </div>
        <div className={styles.grid2}>
          <Card
            title={
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Users size={18} color="#059669" /> For Citizens &amp; Communities
              </span>
            }
          >
            <p>
              Submit infrastructure grievances and local development needs in regional languages using plain text. Each submission receives a persistent reference tracking code to follow administrative analysis transparently.
            </p>
          </Card>
          <Card
            title={
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Building2 size={18} color="#0f172a" /> For Public Decision Makers
              </span>
            }
          >
            <p>
              Review aggregated, structured civic needs linked with baseline census indicators, local asset deficits, and relevant government scheme guidelines to support objective resource allocation.
            </p>
          </Card>
        </div>
      </section>

      {/* Workflow (HOW) */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Evidence-Based Decision Support Pipeline</h2>
          <p className={styles.sectionSubtitle}>
            Step-by-step transformation from unstructured citizen request to policy dossier.
          </p>
        </div>
        <div className={styles.grid4}>
          <div className={styles.flowCard}>
            <span className={styles.flowStep}>STEP 01</span>
            <h3 className={styles.flowTitle}>Citizen Request</h3>
            <p className={styles.flowText}>
              Citizen enters development request in plain text across supported Indian languages.
            </p>
          </div>
          <div className={styles.flowCard}>
            <span className={styles.flowStep}>STEP 02</span>
            <h3 className={styles.flowTitle}>AI Structuring</h3>
            <p className={styles.flowText}>
              Gemini model standardises text, detects location entities, sector taxonomy, and urgency indicators.
            </p>
          </div>
          <div className={styles.flowCard}>
            <span className={styles.flowStep}>STEP 03</span>
            <h3 className={styles.flowTitle}>Public Data Evidence</h3>
            <p className={styles.flowText}>
              Retrieval pipeline links request with local demographic baselines, asset registries, and scheme rules.
            </p>
          </div>
          <div className={styles.flowCard}>
            <span className={styles.flowStep}>STEP 04</span>
            <h3 className={styles.flowTitle}>Decision Support</h3>
            <p className={styles.flowText}>
              Generates an explainable composite priority score and administrative brief for policymakers.
            </p>
          </div>
        </div>
      </section>

      {/* System Integrity & Prototype Notice */}
      <div className={styles.noticeCard}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
          <ShieldCheck size={20} color="#0f172a" style={{ marginTop: '2px', flexShrink: 0 }} />
          <div>
            <h4 className={styles.noticeTitle}>Institutional Decision-Support Prototype Notice</h4>
            <p className={styles.noticeText}>
              NagrikLens AI is an architectural decision-support prototype. It does not replace statutory administrative procedures or make autonomous government decisions. In Phase 1, external datasets and live AI models are unconfigured by default until validated against official guidelines.
            </p>
          </div>
        </div>
      </div>
    </PageContainer>
  );
};
