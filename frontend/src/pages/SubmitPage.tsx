import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Send, Search } from 'lucide-react';
import { PageContainer } from '../components/common/PageContainer';
import { FormField } from '../components/common/FormField';
import { Button } from '../components/common/Button';
import { StatusIndicator } from '../components/common/StatusIndicator';
import styles from './SubmitPage.module.css';

export const SubmitPage: React.FC = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    rawText: '',
    state: 'Maharashtra',
    district: '',
    locality: '',
    category: 'Water',
    affectedHouseholds: '',
  });

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [submittedData, setSubmittedData] = useState<{
    reference_id: string;
    status: string;
    ai_extraction_status: string;
  } | null>(null);

  const categoryOptions = [
    { value: 'Water', label: 'Water (Drinking water, pipeline, contamination)' },
    { value: 'Roads', label: 'Roads & Connectivity (Paved access, potholes, bridges)' },
    { value: 'Healthcare', label: 'Healthcare (PHC, sub-centers, medical equipment)' },
    { value: 'Sanitation', label: 'Sanitation (Drainage, waste management, public toilets)' },
    { value: 'Education', label: 'Education (School facilities, classroom infrastructure)' },
    { value: 'Other', label: 'Other Civic Infrastructure' },
  ];

  const stateOptions = [
    { value: 'Maharashtra', label: 'Maharashtra' },
    { value: 'Karnataka', label: 'Karnataka' },
    { value: 'Uttar Pradesh', label: 'Uttar Pradesh' },
    { value: 'Tamil Nadu', label: 'Tamil Nadu' },
    { value: 'Bihar', label: 'Bihar' },
    { value: 'Madhya Pradesh', label: 'Madhya Pradesh' },
    { value: 'Rajasthan', label: 'Rajasthan' },
    { value: 'West Bengal', label: 'West Bengal' },
    { value: 'Gujarat', label: 'Gujarat' },
    { value: 'Odisha', label: 'Odisha' },
    { value: 'Other', label: 'Other State / UT' },
  ];

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.rawText.trim()) {
      errors.rawText = 'Please provide a description of the civic request.';
    } else if (formData.rawText.trim().length < 5) {
      errors.rawText = 'Request description must be at least 5 characters.';
    }

    if (!formData.state.trim()) {
      errors.state = 'Please select a state.';
    }

    if (!formData.district.trim()) {
      errors.district = 'Please specify the district.';
    }

    if (!formData.locality.trim()) {
      errors.locality = 'Please specify the locality, village, or ward.';
    }

    if (!formData.category.trim()) {
      errors.category = 'Please select a category.';
    }

    if (formData.affectedHouseholds.trim()) {
      const num = Number(formData.affectedHouseholds);
      if (isNaN(num) || num < 0 || !Number.isInteger(num)) {
        errors.affectedHouseholds = 'Please enter a valid non-negative integer.';
      }
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        citizen_request: formData.rawText.trim(),
        state: formData.state.trim(),
        district: formData.district.trim(),
        locality: formData.locality.trim(),
        category: formData.category.trim(),
        affected_households: formData.affectedHouseholds.trim()
          ? parseInt(formData.affectedHouseholds, 10)
          : null,
      };

      const response = await fetch('/api/requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorJson = await response.json().catch(() => ({}));
        throw new Error(errorJson.detail || 'Failed to submit request. Please try again.');
      }

      const data = await response.json();
      setSubmittedData({
        reference_id: data.reference_id,
        status: data.status,
        ai_extraction_status: data.ai_extraction_status || 'NOT_PROCESSED',
      });
    } catch (err: unknown) {
      const error = err as Error;
      setApiError(error.message || 'An unexpected error occurred during submission.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setSubmittedData(null);
    setApiError(null);
    setFieldErrors({});
    setFormData({
      rawText: '',
      state: 'Maharashtra',
      district: '',
      locality: '',
      category: 'Water',
      affectedHouseholds: '',
    });
  };

  return (
    <PageContainer
      title="Citizen Development Request Portal"
      subtitle="Submit public infrastructure needs or civic grievances in plain text across regional languages."
    >
      <div className={styles.formCard}>
        {/* PII & Prototype Advisory Box */}
        <div className={styles.warningBox}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Privacy and Data Minimisation Notice:</strong> This platform is a decision-support prototype for civic need structuring. Do NOT submit sensitive personal identifiers such as Aadhaar numbers, bank account numbers, or personal phone numbers. Describe the community infrastructure issue objectively.
            </div>
          </div>
        </div>

        {apiError && (
          <div className={styles.errorBox}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <div>{apiError}</div>
            </div>
          </div>
        )}

        {submittedData ? (
          <div>
            <div className={styles.successNotice}>
              <div className={styles.successHeader}>
                <CheckCircle2 size={22} color="#059669" />
                <span>Request Submitted</span>
              </div>

              <div className={styles.metaRow}>
                <span>Reference ID:</span>
                <span className={styles.trackingToken}>{submittedData.reference_id}</span>
              </div>

              <div className={styles.metaRow}>
                <span>Status:</span>
                <span className={styles.statusTag}>{submittedData.status}</span>
              </div>

              <div className={styles.metaRow}>
                <span>AI Processing:</span>
                <StatusIndicator
                  status={submittedData.ai_extraction_status === 'PROCESSED' ? 'connected' : 'planned'}
                  label={submittedData.ai_extraction_status}
                />
              </div>

              <p style={{ marginTop: '16px', fontSize: '13px', color: 'var(--slate-700)', fontWeight: 500 }}>
                Save this reference ID to track your request.
              </p>
            </div>

            <div className={styles.successActions}>
              <Button
                variant="primary"
                icon={<Search size={16} />}
                onClick={() => navigate(`/track?ref=${encodeURIComponent(submittedData.reference_id)}`)}
              >
                Track Request
              </Button>
              <Button variant="outline" onClick={handleReset}>
                Submit Another Request
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} noValidate>
            <FormField
              fieldType="textarea"
              label="Citizen Request / Civic Need Description"
              required
              name="rawText"
              value={formData.rawText}
              onChange={handleChange}
              errorText={fieldErrors.rawText}
              placeholder="Describe the issue in English, Hindi, or any regional language (e.g. Ward 4 primary school needs drinking water connection as existing borewell is dry for 3 months...)"
              helperText="You may enter text in your regional language. Google Gemini extracts structured parameters for evidence-based planning."
            />

            <div className={styles.row2}>
              <FormField
                fieldType="select"
                label="State / Union Territory"
                required
                name="state"
                value={formData.state}
                onChange={handleChange}
                errorText={fieldErrors.state}
                options={stateOptions}
              />

              <FormField
                fieldType="input"
                label="District"
                required
                name="district"
                value={formData.district}
                onChange={handleChange}
                errorText={fieldErrors.district}
                placeholder="e.g. Pune"
              />
            </div>

            <div className={styles.row2}>
              <FormField
                fieldType="input"
                label="Locality / Village / Ward"
                required
                name="locality"
                value={formData.locality}
                onChange={handleChange}
                errorText={fieldErrors.locality}
                placeholder="e.g. Ward 4, Ambedkar Nagar"
              />

              <FormField
                fieldType="select"
                label="Primary Category"
                required
                name="category"
                value={formData.category}
                onChange={handleChange}
                errorText={fieldErrors.category}
                options={categoryOptions}
              />
            </div>

            <FormField
              fieldType="input"
              type="number"
              label="Estimated Affected Households (Optional)"
              name="affectedHouseholds"
              value={formData.affectedHouseholds}
              onChange={handleChange}
              errorText={fieldErrors.affectedHouseholds}
              placeholder="e.g. 150"
              helperText="Approximate number of local residents or families impacted by this infrastructure need."
            />

            <div className={styles.formActions}>
              <Button
                type="submit"
                variant="primary"
                disabled={isSubmitting}
                icon={<Send size={15} />}
              >
                {isSubmitting ? 'Submitting Request...' : 'Submit Request'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </PageContainer>
  );
};
