import { forwardRef, type InputHTMLAttributes, type ReactNode, type TextareaHTMLAttributes } from 'react'

import { classNames } from '../utils/classNames'

type CommonProps = {
  label: string
  hint?: string | undefined
  error?: string | undefined
  className?: string | undefined
  action?: ReactNode | undefined
}

type InputFieldProps = CommonProps & InputHTMLAttributes<HTMLInputElement>

type TextAreaFieldProps = CommonProps & TextareaHTMLAttributes<HTMLTextAreaElement>

const inputBaseClassName =
  'mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-400 focus:ring-4 focus:ring-sky-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-500'

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(function InputField(
  { label, hint, error, className, action, ...inputProps },
  ref,
) {
  return (
    <label className={classNames('block', className)}>
      <div className="flex items-center justify-between gap-3 text-sm font-medium text-slate-700 dark:text-slate-200">
        <span>{label}</span>
        {action}
      </div>
      <input ref={ref} className={inputBaseClassName} {...inputProps} />
      {hint && !error ? <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{hint}</p> : null}
      {error ? <p className="mt-2 text-xs font-medium text-rose-500">{error}</p> : null}
    </label>
  )
})

export const TextAreaField = forwardRef<HTMLTextAreaElement, TextAreaFieldProps>(function TextAreaField(
  { label, hint, error, className, action, ...textAreaProps },
  ref,
) {
  return (
    <label className={classNames('block', className)}>
      <div className="flex items-center justify-between gap-3 text-sm font-medium text-slate-700 dark:text-slate-200">
        <span>{label}</span>
        {action}
      </div>
      <textarea ref={ref} className={classNames(inputBaseClassName, 'min-h-32 resize-y')} {...textAreaProps} />
      {hint && !error ? <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{hint}</p> : null}
      {error ? <p className="mt-2 text-xs font-medium text-rose-500">{error}</p> : null}
    </label>
  )
})