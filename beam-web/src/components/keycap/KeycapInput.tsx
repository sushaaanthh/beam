import type { InputHTMLAttributes } from 'react'
import { useId } from 'react'
import { classNames } from '../../utils/classNames'

type KeycapInputProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> & {
  label: string
  hint?: string
  error?: string
}

export function KeycapInput({ label, hint, error, className, ...props }: KeycapInputProps) {
  const id = useId()
  const hintId = `${id}-hint`
  const describedBy = error ? `${id}-error` : hint ? hintId : undefined

  return (
    <div className="flex w-full flex-col gap-2">
      <label htmlFor={id} className="text-[11px] font-medium uppercase tracking-[0.14em] text-dim">
        {label}
      </label>
      <input
        id={id}
        className={classNames('kc-input', className)}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        {...props}
      />
      {error ? (
        <p id={`${id}-error`} role="alert" className="text-xs text-[#FF8A8A]">
          {error}
        </p>
      ) : hint ? (
        <p id={hintId} className="text-xs text-dim">
          {hint}
        </p>
      ) : null}
    </div>
  )
}
