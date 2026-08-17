import { forwardRef, type InputHTMLAttributes, type ReactNode, type TextareaHTMLAttributes } from 'react'

type CommonProps = {
  label?: string
  hint?: string
  error?: string
  className?: string
  action?: ReactNode
}

export type InputFieldProps = CommonProps & InputHTMLAttributes<HTMLInputElement>
export type TextAreaFieldProps = CommonProps & TextareaHTMLAttributes<HTMLTextAreaElement>

const inputBaseClassName = `
  w-full rounded-lg bg-[#0C0C0C] border border-[#222222]
  px-3.5 py-2.5 text-sm text-[#F5F5F0] font-ui
  placeholder:text-[#555552]
  shadow-[inset_0_2px_4px_rgba(0,0,0,0.6)]
  transition-all duration-150 ease-out
  hover:border-[#333333]
  focus:border-[#C7FF4A] focus:outline-none focus:ring-1 focus:ring-[#C7FF4A]
  disabled:opacity-40 disabled:cursor-not-allowed
`

const labelClassName = `
  block text-[11px] font-medium tracking-[0.08em] text-[#B8B8B0]
  uppercase mb-1.5
`

const hintClassName = 'mt-1.5 text-xs text-[#73736F]'
const errorClassName = 'mt-1.5 text-xs font-medium text-[#FF6B6B]'

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
  function InputField(
    { label, hint, error, className = '', action, id, ...inputProps },
    ref
  ) {
    const inputId = id || (label ? `input-${label.toLowerCase().replace(/\s+/g, '-')}` : undefined)
    const errorId = error && inputId ? `${inputId}-error` : undefined
    const hintId = hint && !error && inputId ? `${inputId}-hint` : undefined

    return (
      <div className={`space-y-1 ${className}`}>
        {label && (
          <div className="flex items-center justify-between">
            <label htmlFor={inputId} className={labelClassName}>
              {label}
            </label>
            {action && <div className="text-xs text-[#73736F]">{action}</div>}
          </div>
        )}
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            className={`${inputBaseClassName} ${error ? 'border-[#5A2222] focus:border-[#FF6B6B] focus:ring-[#FF6B6B]' : ''}`}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={errorId || hintId}
            {...inputProps}
          />
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

export const TextAreaField = forwardRef<HTMLTextAreaElement, TextAreaFieldProps>(
  function TextAreaField(
    { label, hint, error, className = '', action, id, ...textAreaProps },
    ref
  ) {
    const inputId = id || (label ? `textarea-${label.toLowerCase().replace(/\s+/g, '-')}` : undefined)
    const errorId = error && inputId ? `${inputId}-error` : undefined
    const hintId = hint && !error && inputId ? `${inputId}-hint` : undefined

    return (
      <div className={`space-y-1 ${className}`}>
        {label && (
          <div className="flex items-center justify-between">
            <label htmlFor={inputId} className={labelClassName}>
              {label}
            </label>
            {action && <div className="text-xs text-[#73736F]">{action}</div>}
          </div>
        )}
        <div className="relative">
          <textarea
            ref={ref}
            id={inputId}
            className={`${inputBaseClassName} min-h-[120px] resize-y ${error ? 'border-[#5A2222] focus:border-[#FF6B6B] focus:ring-[#FF6B6B]' : ''}`}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={errorId || hintId}
            {...textAreaProps}
          />
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