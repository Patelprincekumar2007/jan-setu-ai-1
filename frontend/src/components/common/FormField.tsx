import React from 'react';
import styles from './FormField.module.css';

interface BaseFieldProps {
  label: string;
  required?: boolean;
  helperText?: string;
  errorText?: string;
  id?: string;
}

interface InputFieldProps extends BaseFieldProps, React.InputHTMLAttributes<HTMLInputElement> {
  fieldType?: 'input';
}

interface TextareaFieldProps extends BaseFieldProps, React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  fieldType: 'textarea';
}

interface SelectFieldProps extends BaseFieldProps, React.SelectHTMLAttributes<HTMLSelectElement> {
  fieldType: 'select';
  options: Array<{ value: string; label: string }>;
}

type FormFieldProps = InputFieldProps | TextareaFieldProps | SelectFieldProps;

export const FormField: React.FC<FormFieldProps> = (props) => {
  const { label, required, helperText, errorText, id, fieldType = 'input', ...rest } = props;
  const inputId = id || label.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className={styles.fieldGroup}>
      <label htmlFor={inputId} className={styles.label}>
        {label}
        {required && <span className={styles.required}>*</span>}
      </label>

      {fieldType === 'input' && (
        <input
          id={inputId}
          className={styles.input}
          {...(rest as React.InputHTMLAttributes<HTMLInputElement>)}
        />
      )}

      {fieldType === 'textarea' && (
        <textarea
          id={inputId}
          className={styles.textarea}
          {...(rest as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
        />
      )}

      {fieldType === 'select' && (
        <select
          id={inputId}
          className={styles.select}
          {...(rest as React.SelectHTMLAttributes<HTMLSelectElement>)}
        >
          {(props as SelectFieldProps).options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      )}

      {helperText && !errorText && <span className={styles.helper}>{helperText}</span>}
      {errorText && <span className={styles.error}>{errorText}</span>}
    </div>
  );
};
