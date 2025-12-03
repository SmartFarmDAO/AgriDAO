import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen items-center justify-center p-4">
          <div className="max-w-md rounded-lg border border-red-200 bg-red-50 p-6">
            <h2 className="mb-2 text-xl font-semibold text-red-700">Something went wrong</h2>
            <p className="mb-4 text-red-600">{this.state.error?.message || 'An unexpected error occurred'}</p>
            <details className="mb-4">
              <summary className="cursor-pointer text-sm text-red-600">Error details</summary>
              <pre className="mt-2 overflow-auto text-xs text-red-500">
                {this.state.error?.stack}
              </pre>
            </details>
            <button
              onClick={() => window.location.reload()}
              className="rounded bg-red-100 px-4 py-2 text-red-700 hover:bg-red-200"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
