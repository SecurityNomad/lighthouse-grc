import api from './client'

export interface UserRead {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string | null
}

export interface UserCreate {
  email: string
  full_name: string
  role: string
  password: string
}

export interface UserUpdate {
  full_name?: string
  role?: string
  is_active?: boolean
  password?: string
}

export const adminApi = {
  listUsers: (): Promise<UserRead[]> =>
    api.get('/api/v1/admin/users').then(r => r.data),

  createUser: (data: UserCreate): Promise<UserRead> =>
    api.post('/api/v1/admin/users', data).then(r => r.data),

  updateUser: (id: string, data: UserUpdate): Promise<UserRead> =>
    api.patch(`/api/v1/admin/users/${id}`, data).then(r => r.data),

  deleteUser: (id: string): Promise<void> =>
    api.delete(`/api/v1/admin/users/${id}`),

  changePassword: (current_password: string, new_password: string): Promise<void> =>
    api.post('/api/v1/auth/change-password', { current_password, new_password }).then(r => r.data),
}
