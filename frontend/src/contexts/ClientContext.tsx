import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { clientsApi, type Client } from '../api/clients'
import { useAuth } from './AuthContext'

interface ClientContextType {
  clients: Client[]
  selectedClient: Client | null
  selectClient: (client: Client | null) => void
  isLoading: boolean
}

const ClientContext = createContext<ClientContextType | null>(null)

export function ClientProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  const [selectedClient, setSelectedClient] = useState<Client | null>(null)

  const { data: clients = [], isLoading } = useQuery({
    queryKey: ['clients'],
    queryFn: clientsApi.list,
    enabled: isAuthenticated,
  })

  // Restore last selected client from localStorage
  useEffect(() => {
    if (clients.length === 0) return
    const savedId = localStorage.getItem('lh_client_id')
    if (savedId) {
      const found = clients.find(c => c.id === savedId)
      if (found) setSelectedClient(found)
    }
  }, [clients])

  const selectClient = useCallback((client: Client | null) => {
    setSelectedClient(client)
    if (client) {
      localStorage.setItem('lh_client_id', client.id)
    } else {
      localStorage.removeItem('lh_client_id')
    }
  }, [])

  return (
    <ClientContext.Provider value={{ clients, selectedClient, selectClient, isLoading }}>
      {children}
    </ClientContext.Provider>
  )
}

export function useClient() {
  const ctx = useContext(ClientContext)
  if (!ctx) throw new Error('useClient must be used within ClientProvider')
  return ctx
}
