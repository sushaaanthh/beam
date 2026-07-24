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
  'mt-2 w-full rounded-[1rem] border border-white/10 bg-white/4 px-4 py-3 text-sm text-white/92 outline-none transition duration-200 placeholder:text-white/34 hover:border-white/16 focus:border-white/20 focus:bg-white/6 focus:ring-2 focus:ring-white/12'

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(function InputField(
  { label, hint, error, className, action, ...inputProps },
  ref,
) {
  return (
    <label className={classNames('block', className)}>
      <div className="flex items-center justify-between gap-3 text-sm font-medium text-white/88">
        <span>{label}</span>
        {action}
      </div>
      <input ref={ref} className={inputBaseClassName} {...inputProps} />
      {hint && !error ? <p className="mt-2 text-xs text-white/54">{hint}</p> : null}
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
      <div className="flex items-center justify-between gap-3 text-sm font-medium text-white/88">
        <span>{label}</span>
        {action}
      </div>
      <textarea ref={ref} className={classNames(inputBaseClassName, 'min-h-32 resize-y')} {...textAreaProps} />
      {hint && !error ? <p className="mt-2 text-xs text-white/54">{hint}</p> : null}
      {error ? <p className="mt-2 text-xs font-medium text-rose-500">{error}</p> : null}
    </label>
  )
})

export function KeycapInputField(props: InputFieldProps) {
  return <InputField {...props} />
}

export function KeycapTextAreaField(props: TextAreaFieldProps) {
  return <TextAreaField {...props} />
}