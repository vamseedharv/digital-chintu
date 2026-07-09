import { isRouteErrorResponse, useRouteError } from 'react-router'
import { AlertTriangle } from 'lucide-react'
import { EmptyState } from '../components/ui/EmptyState'
import { LinkButton } from '../components/ui/LinkButton'

export function ErrorPage() {
  const error = useRouteError()

  const description = isRouteErrorResponse(error)
    ? `${error.status} ${error.statusText}`
    : 'An unexpected error occurred. Try reloading the page.'

  return (
    <EmptyState
      icon={AlertTriangle}
      title="Something went wrong"
      description={description}
      action={<LinkButton to="/">Back to Home</LinkButton>}
    />
  )
}
