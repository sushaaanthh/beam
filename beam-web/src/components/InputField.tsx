import { forwardRef, type InputHTMLAttributes, type ReactNode, type TextareaHTMLAttributes } from 'react'

type CommonProps = {
  label: string
  hint?: string
  error?: string
  className?: string
  action?: ReactNode
}

type InputFieldProps = CommonProps & InputHTMLAttributes<HTMLInputElement>

type TextAreaFieldProps = CommonProps & TextareaHTMLAttributes<HTMLTextAreaElement>

const inputBaseClassName = `
  w-full rounded-apple-md
  bg-apple-bg border border-apple-border
  px-4 py-3 text-body-md text-apple-textPrimary
  placeholder:text-apple-textTertiary
  outline-none
  transition-all duration-apple-fast ease-apple
  hover:border-apple-borderHover hover:bg-apple-bgCard
  focus:border-apple-accent focus:ring-2 focus:ring-apple-accent/20 focus:bg-apple-bg
  disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-apple-border
  error:border-apple-danger error:focus:border-apple-danger error:focus:ring-apple-danger/20
`

const labelClassName = `
  block text-caption-lg font-semibold tracking-wide text-apple-textSecondary
  uppercase mb-2
`

const hintClassName = 'mt-2 text-caption-md text-apple-textTertiary'
const errorClassName = 'mt-2 text-caption-md font-medium text-apple-danger'
const actionClassName = 'text-caption-lg font-medium text-apple-accent hover:text-apple-accentLight transition-colors'

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
  function InputField(
    { label, hint, error, className, action, id, ...inputProps },
    ref
  ) {
    const inputId = id || `input-${label.toLowerCase().replace(/\s+/g, '-')}`
    const errorId = error ? `${inputId}-error` : undefined
    const hintId = hint && !error ? `${inputId}-hint` : undefined

    return (
      <label className={className} htmlFor={inputId}>
        <span className={labelClassName}>{label}</span>
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            className={`${inputBaseClassName} ${error ? 'error' : ''}`}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={errorId || hintId}
            {...inputProps}
          />
          {action && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-apple-textTertiary">
              {action}
            </div>
          )}
        </div>
        {error ? (
          <p id={errorId} className={errorClassName} role="alert">
            {error}
          </p>
        ) : hint ? (
          <p id={hintId} className={hintClassName}>
            {hint}
          </p>
        ) : null}
      </label>
    )
  }
)

export const TextAreaField = forwardRef<HTMLTextAreaElement, TextAreaFieldProps>(
  function TextAreaField(
    { label, hint, error, className, action, id, ...textAreaProps },
    ref
  ) {
    const inputId = id || `textarea-${label.toLowerCase().replace(/\s+/g, '-')}`
    const errorId = error ? `${inputId}-error` : undefined
    const hintId = hint && !error ? `${inputId}-hint` : undefined

    return (
      <label className={className} htmlFor={inputId}>
        <span className={labelClassName}>{label}</span>
        <div className="relative">
          <textarea
            ref={ref}
            id={inputId}
            className={`${inputBaseClassName} min-h-[120px] resize-y ${error ? 'error' : ''}`}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={errorId || hintId}
            {...textAreaProps}
          />
          {action && (
            <div className="absolute right-4 top-4 text-apple-textTertiary">
              {action}
            </div>
          )}
        </div>
        {error ? (
          <p id={errorId} className={errorClassName} role="alert">
            {error}
          </p>
        ) : hint ? (
          <p id={hintId} className={hintClassName}>
            {hint}
          </p>
        ) : null}
      </label>
    )
  }
)

// Apple-style floating label input variant
type FloatingInputProps = CommonProps & InputHTMLAttributes<HTMLInputElement> & {
  placeholder?: string
}

export const FloatingInputField = forwardRef<HTMLInputElement, FloatingInputProps>(
  function FloatingInputField(
    { label, hint, error, className, placeholder, id, ...inputProps },
    ref
  ) {
    const inputId = id || `floating-input-${label.toLowerCase().replace(/\s+/g, '-')}`
    const errorId = error ? `${inputId}-error` : undefined
    const hintId = hint && !error ? `${inputId}-hint` : undefined
    const hasValue = inputProps.value || inputProps.defaultValue

    return (
      <div className={className}>
        <div className="relative group">
          <input
            ref={ref}
            id={inputId}
            className={`
              w-full rounded-apple-md
              bg-apple-bg border border-apple-border
              px-4 py-4 text-body-md text-apple-textPrimary
              outline-none
              transition-all duration-apple-fast ease-apple
              hover:border-apple-borderHover hover:bg-apple-bgCard
              focus:border-apple-accent focus:ring-2 focus:ring-apple-accent/20 focus:bg-apple-bg
              disabled:opacity-40 disabled:cursor-not-allowed
              peer
              ${error ? 'border-apple-danger focus:border-apple-danger focus:ring-apple-danger/20' : ''}
              ${hasValue ? 'pt-6 pb-2' : ''}
            `}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={errorId || hintId}
            placeholder=" "
            {...inputProps}
          />
          <label
            htmlFor={inputId}
            className={`
              absolute left-4 top-1/2 -translate-y-1/2
              text-body-md text-apple-textTertiary
              pointer-events-none
              transition-all duration-apple-fast ease-apple
              peer-focus:top-2 peer-focus:-translate-y-3 peer-focus:text-caption-lg peer-focus:text-apple-accent
              peer-[&:not(:placeholder-shown)]:top-2 peer-[&:not(:placeholder-shown)]:-translate-y-3 peer-[&:not(:placeholder-shown)]:text-caption-lg peer-[&:not(:placeholder-shown)]:text-apple-textSecondary
              ${hasValue ? 'top-2 -translate-y-3 text-caption-lg text-apple-textSecondary' : ''}
            `}
          >
            {label}
          </label>
          {action && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-apple-textTertiary">
              {action}
            </div>
          )}
        </div>
        {error ? (
          <p id={errorId} className={errorClassName} role="alert">
            {error}
          </p>
        ) : hint ? (
          <p id={hintId} className={hintClassName}>
            {hint}
          </p>
        ) : null}
      </div>
    )
  }
)

export function KeycapInputField(props: InputFieldProps) {
  return <InputField {...props} />
}

export function KeycapTextAreaField(props: TextAreaFieldProps) {
  return <TextAreaField {...props} />
}