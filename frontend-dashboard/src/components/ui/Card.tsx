import clsx from 'clsx'
import { motion } from 'framer-motion'
import type { HTMLMotionProps } from 'framer-motion'

export function Card({ className, children, ...props }: HTMLMotionProps<'div'>) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={clsx('glass rounded-2xl p-6 shadow-sm', className)}
      {...props}
    >
      {children}
    </motion.div>
  )
}
