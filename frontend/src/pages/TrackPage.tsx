import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, FileSearch, AlertCircle } from 'lucide-react';
import { PageContainer } from '../components/common/PageContainer';
import { FormField } from '../components/common/FormField';
import { Button } from '../components/common/Button';
import { StatusIndicator } from '../components/common/StatusIndicator';
import styles from './TrackPage.module.css';

interface RequestDetail {
  reference_id: string;
  status: string;
  created_at: string;
  category: string;
  location: {
    state: string;
    district: string;
    locality: string;
  };
}

export const TrackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [referenceId, setReferenceId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const [requestDetail, setRequestDetail] = useState<RequestDetail | null>(null);

  const fetchRequest = async (ref: string) => {
    const trimmed = ref.trim().toUpperCase();
    if (!trimmed) return;

    setIsLoading(true);
    setHasSearched(true);
    setNotFound(false);
    setRequestDetail(null);

    try {
      const response = await fetch(`/api/requests/${encodeURIComponent(trimmed)}`);
      if (response.status === 404) {
        setNotFound(true);
      } else if (!response.ok) {
        setNotFound(true);
      } else {
        const data = await response.json();
        setRequestDetail(data);
      }
    } catch {
      setNotFound(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const refParam = searchParams.get('ref');
    if (refParam) {
      setReferenceId(refParam);
      fetchRequest(refParam);
    }
  }, [searchParams]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!referenceId.trim()) return;
    fetchRequest(referenceId);
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <PageContainer
      title="Application Status Tracker"
      subtitle="Verify the processing lifecycle and registration status of your submitted civic request."
    >
      <div className={styles.container}>
        <div className={styles.searchBox}>
          <form onSubmit={handleSearch} className={styles.searchForm}>
            <div className={styles.inputWrapper}>
              <FormField
                fieldType="input"
                label="Enter Reference Tracking Code"
                placeholder="e.g. NL-20260928-842910"
                value={referenceId}
                onChange={(e) => setReferenceId(e.target.value)}
                helperText="Reference codes are generated upon submitting a civic request via the portal."
              />
            </div>
            <div style={{ marginBottom: '20px' }}>
              <Button
                type="submit"
                variant="primary"
                disabled={isLoading}
                icon={<Search size={15} />}
              >
                {isLoading ? 'Searching...' : 'Track Request'}
              </Button>
            </div>
          </form>
        </div>

        {requestDetail && (
          <div className={styles.resultCard}>
            <div className={styles.resultHeader}>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--slate-500)', display: 'block', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Reference Tracking Code
                </span>
                <span className={styles.refToken}>{requestDetail.reference_id}</span>
              </div>
              <div>
                <StatusIndicator
                  status={requestDetail.status.toLowerCase() === 'received' ? 'pending' : 'info'}
                  label={requestDetail.status}
                />
              </div>
            </div>

            <div className={styles.metaGrid}>
              <div className={styles.metaItem}>
                <span className={styles.metaLabel}>Submission Date</span>
                <span className={styles.metaValue}>{formatDate(requestDetail.created_at)}</span>
              </div>

              <div className={styles.metaItem}>
                <span className={styles.metaLabel}>Primary Category</span>
                <span className={styles.metaValue}>{requestDetail.category}</span>
              </div>

              <div className={styles.metaItem}>
                <span className={styles.metaLabel}>Location Division</span>
                <span className={styles.metaValue}>
                  {requestDetail.location.locality}, {requestDetail.location.district}
                </span>
              </div>

              <div className={styles.metaItem}>
                <span className={styles.metaLabel}>State / UT</span>
                <span className={styles.metaValue}>{requestDetail.location.state}</span>
              </div>
            </div>

            <div className={styles.infoBanner}>
              <strong>Current Stage: RECEIVED</strong> &bull; Your civic request has been recorded in the system. In future phases, it will undergo Gemini multilingual extraction and RAG public data alignment.
            </div>
          </div>
        )}

        {notFound && (
          <div className={styles.notFoundState}>
            <div className={styles.notFoundIcon}>
              <AlertCircle size={24} />
            </div>
            <h3 className={styles.notFoundTitle}>Request not found</h3>
            <p className={styles.notFoundText}>
              No record was found for reference code <strong>"{referenceId}"</strong>. Please verify the code and try again.
            </p>
          </div>
        )}

        {!hasSearched && !requestDetail && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>
              <FileSearch size={24} />
            </div>
            <h3 className={styles.emptyTitle}>No tracking query initiated</h3>
            <p className={styles.emptyText}>
              Enter a valid reference ID above to inspect the registration status and administrative metadata for your request.
            </p>
          </div>
        )}
      </div>
    </PageContainer>
  );
};
