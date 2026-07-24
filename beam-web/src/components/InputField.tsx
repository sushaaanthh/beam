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
  'kds-inset mt-2 w-full rounded-[14px] px-4 py-3 text-sm text-white/92 outline-none transition duration-150 placeholder:text-white/30 hover:border-white/16 focus:border-[#b2ff7d]/55 focus:ring-2 focus:ring-[#b2ff7d]/10'

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
