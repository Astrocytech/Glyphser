import { Component, ReactNode } from 'react'
import { Button } from '@/components/ui/button'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.state.error) {
        console.error('Error:', this.state.error.message, this.state.error.stack)
      }
      return (
        this.props.fallback || (
          <div className="flex min-h-[400px] items-center justify-center">
            <div className="text-center space-y-4 p-8">
              <div className="text-destructive text-lg font-medium">Something went wrong</div>
              <p className="text-muted-foreground text-sm">
                An unexpected error occurred. Please try again.
              </p>
              <Button variant="outline" onClick={this.handleReset}>
                Try again
              </Button>
            </div>
          </div>
        )
      )
    }

    return this.props.children
  }
}