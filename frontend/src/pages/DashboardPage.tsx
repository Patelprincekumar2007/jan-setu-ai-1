import React from 'react';
import { Filter, RefreshCw } from 'lucide-react';
import { PageContainer } from '../components/common/PageContainer';
import { Button } from '../components/common/Button';
import { Table } from '../components/common/Table';
import type { Column } from '../components/common/Table';
import { StatusIndicator } from '../components/common/StatusIndicator';
import styles from './DashboardPage.module.css';

interface RequestItem {
  id: string;
  trackingCode: string;
  state: string;
  district: string;
  locality: string;
  sector: string;
  priorityScore: number;
  status: string;
}

export const DashboardPage: React.FC = () => {
  // Empty dataset for Phase 1 (No fabricated records)
  const requests: RequestItem[] = [];

  const columns: Column<RequestItem>[] = [
    { key: 'trackingCode', header: 'Reference ID', width: '150px' },
    {
      key: 'location',
      header: 'Administrative Division',
      render: (row) => `${row.locality}, ${row.district}, ${row.state}`,
    },
    { key: 'sector', header: 'Sector Taxonomy' },
    {
      key: 'priorityScore',
      header: 'Priority Score (0-100)',
      render: (row) => `${row.priorityScore}/100`,
    },
    {
      key: 'status',
      header: 'Review Status',
      render: () => <StatusIndicator status="planned" label="Awaiting Ingestion" />,
    },
  ];

  return (
    <PageContainer
      title="Officer Intelligence Dashboard"
      subtitle="Administrative decision-support queue for civic request prioritisation and scheme alignment."
      headerAction={
        <Button variant="outline" size="sm" icon={<RefreshCw size={14} />}>
          Refresh Queue
        </Button>
      }
    >
      {/* Metric Counters - Strictly 0 / Awaiting Phase 2-6 Data */}
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricLabel}>Total Ingested Requests</div>
          <div className={styles.metricValue}>0</div>
          <div className={styles.metricNote}>Awaiting Phase 2 ingestion</div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricLabel}>High Priority Interventions</div>
          <div className={styles.metricValue}>0</div>
          <div className={styles.metricNote}>Awaiting scoring engine</div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricLabel}>Verified Ground Deficits</div>
          <div className={styles.metricValue}>0</div>
          <div className={styles.metricNote}>Awaiting census baseline sync</div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricLabel}>Scheme Matched Dossiers</div>
          <div className={styles.metricValue}>0</div>
          <div className={styles.metricNote}>Awaiting RAG pipeline</div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className={styles.toolbar}>
        <div className={styles.filterGroup}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--slate-500)' }}>
            <Filter size={14} /> Filters:
          </div>
          <select className={styles.filterSelect} disabled aria-label="Filter by Sector">
            <option>All Sectors</option>
          </select>
          <select className={styles.filterSelect} disabled aria-label="Filter by State">
            <option>All States</option>
          </select>
          <select className={styles.filterSelect} disabled aria-label="Filter by Urgency">
            <option>All Urgency Levels</option>
          </select>
        </div>
        <div style={{ fontSize: '12px', color: 'var(--slate-400)' }}>
          Showing 0 of 0 records
        </div>
      </div>

      {/* Action Queue Table with explicit Empty State */}
      <div style={{ marginTop: '16px' }}>
        <Table
          columns={columns}
          data={requests}
          keyExtractor={(row) => row.id}
          emptyMessage="No analysed requests yet. Citizen submissions will appear here once processed by the Gemini extraction pipeline."
        />
      </div>
    </PageContainer>
  );
};
