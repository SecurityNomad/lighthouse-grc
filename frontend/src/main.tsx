import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider, MutationCache } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import { ClientProvider } from './contexts/ClientContext'
import Toaster from './components/Toaster'
import { pushToast } from './lib/toast'
import { getErrorMessage } from './lib/errors'
import App from './App.tsx'
import './index.css'

// Surface every failed mutation as a toast. Individual mutations may still add
// their own onError (it runs in addition to this) but no failure is silent.
const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onError: (error) => pushToast(getErrorMessage(error), 'error'),
  }),
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ClientProvider>
          <App />
          <Toaster />
        </ClientProvider>
      </AuthProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)
