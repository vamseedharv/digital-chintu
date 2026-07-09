import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router'
import { MotionConfig } from 'framer-motion'
import './index.css'
import { router } from './app/router.tsx'
import { ThemeProvider } from './theme/ThemeProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* reducedMotion="user" makes every Framer Motion animation in the app
        respect prefers-reduced-motion automatically, in one place. */}
    <MotionConfig reducedMotion="user">
      <ThemeProvider>
        <RouterProvider router={router} />
      </ThemeProvider>
    </MotionConfig>
  </StrictMode>,
)
