import clsx from 'clsx'

type Size = 'sm' | 'md' | 'lg'

interface LoadingProps {
  size?: Size
  text?: string
  fullPage?: boolean
}

const sizeMap: Record<Size, string> = {
  sm: 'h-5 w-5 border-2',
  md: 'h-10 w-10 border-4',
  lg: 'h-16 w-16 border-4',
}

export default function Loading({ size = 'md', text, fullPage = false }: LoadingProps) {
  return (
    <div
      className={clsx(
        'flex flex-col items-center justify-center gap-3',
        fullPage && 'min-h-screen',
        !fullPage && 'py-12',
      )}
    >
      <div
        className={clsx(
          'animate-spin rounded-full border-info-500 border-t-transparent',
          sizeMap[size],
        )}
      />
      {text && <p className="text-sm text-gray-500 dark:text-gray-400">{text}</p>}
    </div>
  )
}
