import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { adminApi, type UserRead, type UserCreate, type UserUpdate } from '../api/admin'
import { useAuth } from '../contexts/AuthContext'
import { UserPlus, ShieldCheck, KeyRound, User, ToggleLeft, ToggleRight, Trash2 } from 'lucide-react'

type Tab = 'users' | 'account'

/* ── Shared helpers ─────────────────────────────────────────── */

function RoleBadge({ role }: { role: string }) {
  return (
    <span className={`badge ${role === 'admin' ? 'badge-indigo' : 'badge-gray'}`}>
      {role}
    </span>
  )
}

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span className={`badge ${active ? 'badge-green' : 'badge-gray'}`}>
      {active ? 'Active' : 'Inactive'}
    </span>
  )
}

/* ── Create User Modal ──────────────────────────────────────── */

function CreateUserModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<UserCreate>({
    defaultValues: { role: 'analyst' },
  })

  const createMut = useMutation({
    mutationFn: adminApi.createUser,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['adminUsers'] }); onClose() },
  })

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-md">
        <div className="modal-header">
          <h2 className="modal-title">Create User</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(data => createMut.mutate(data))}>
          <div className="modal-body">
            <div>
              <label className="form-label">Full Name <span className="text-red-500">*</span></label>
              <input {...register('full_name', { required: 'Required' })} className="neu-input" />
              {errors.full_name && <p className="text-xs text-red-500 mt-1">{errors.full_name.message}</p>}
            </div>
            <div>
              <label className="form-label">Email <span className="text-red-500">*</span></label>
              <input {...register('email', { required: 'Required' })} type="email" className="neu-input" />
              {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>}
            </div>
            <div>
              <label className="form-label">Role</label>
              <select {...register('role')} className="neu-select">
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div>
              <label className="form-label">Password <span className="text-red-500">*</span></label>
              <input {...register('password', { required: 'Required', minLength: { value: 8, message: 'Min 8 characters' } })} type="password" className="neu-input" />
              {errors.password && <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>}
            </div>
            {createMut.error && (
              <p className="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
                {(createMut.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Failed to create user'}
              </p>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button type="submit" disabled={isSubmitting || createMut.isPending} className="btn-primary">
              Create User
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ── Edit User Modal ────────────────────────────────────────── */

function EditUserModal({ user, onClose }: { user: UserRead; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<UserUpdate>({
    defaultValues: { full_name: user.full_name, role: user.role },
  })

  const updateMut = useMutation({
    mutationFn: (data: UserUpdate) => adminApi.updateUser(user.id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['adminUsers'] }); onClose() },
  })

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-sm">
        <div className="modal-header">
          <h2 className="modal-title">Edit User</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(data => updateMut.mutate(data))}>
          <div className="modal-body">
            <div>
              <label className="form-label">Full Name</label>
              <input {...register('full_name')} className="neu-input" />
            </div>
            <div>
              <label className="form-label">Role</label>
              <select {...register('role')} className="neu-select">
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            {updateMut.error && (
              <p className="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
                {(updateMut.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Failed to update user'}
              </p>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button type="submit" disabled={isSubmitting || updateMut.isPending} className="btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ── Set Password Modal ─────────────────────────────────────── */

function SetPasswordModal({ user, onClose }: { user: UserRead; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<{ password: string; confirm: string }>()

  const updateMut = useMutation({
    mutationFn: (password: string) => adminApi.updateUser(user.id, { password }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['adminUsers'] }); onClose() },
  })

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-sm">
        <div className="modal-header">
          <h2 className="modal-title">Set Password</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(data => updateMut.mutate(data.password))}>
          <div className="modal-body">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Setting new password for <span className="font-semibold text-slate-700 dark:text-slate-300">{user.full_name}</span>
            </p>
            <div>
              <label className="form-label">New Password <span className="text-red-500">*</span></label>
              <input
                {...register('password', { required: 'Required', minLength: { value: 8, message: 'Min 8 characters' } })}
                type="password"
                className="neu-input"
              />
              {errors.password && <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>}
            </div>
            <div>
              <label className="form-label">Confirm Password <span className="text-red-500">*</span></label>
              <input
                {...register('confirm', {
                  required: 'Required',
                  validate: v => v === watch('password') || 'Passwords do not match',
                })}
                type="password"
                className="neu-input"
              />
              {errors.confirm && <p className="text-xs text-red-500 mt-1">{errors.confirm.message}</p>}
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button type="submit" disabled={isSubmitting || updateMut.isPending} className="btn-primary">Set Password</button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ── Users Tab ──────────────────────────────────────────────── */

function UsersTab() {
  const qc = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [editUser, setEditUser] = useState<UserRead | null>(null)
  const [setPassUser, setSetPassUser] = useState<UserRead | null>(null)

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['adminUsers'],
    queryFn: adminApi.listUsers,
  })

  const toggleMut = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      adminApi.updateUser(id, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['adminUsers'] }),
  })

  const deleteMut = useMutation({
    mutationFn: adminApi.deleteUser,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['adminUsers'] }),
  })

  return (
    <>
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="section-title">User Accounts</h2>
          <p className="text-xs text-slate-400 mt-0.5">{users.length} user{users.length !== 1 ? 's' : ''} registered</p>
        </div>
        <button onClick={() => setCreateOpen(true)} className="btn-primary flex items-center gap-2">
          <UserPlus size={15} />
          New User
        </button>
      </div>

      {isLoading ? (
        <div className="text-sm text-slate-400 text-center py-12">Loading…</div>
      ) : (
        <div className="neu-table-wrap">
          <table className="neu-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="group">
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center shrink-0">
                        <User size={13} className="text-indigo-600 dark:text-indigo-400" />
                      </div>
                      <span className="font-medium text-slate-900 dark:text-slate-100">{u.full_name}</span>
                    </div>
                  </td>
                  <td className="text-slate-500 dark:text-slate-400">{u.email}</td>
                  <td><RoleBadge role={u.role} /></td>
                  <td><StatusBadge active={u.is_active} /></td>
                  <td className="text-xs text-slate-400">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                  </td>
                  <td>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => setEditUser(u)}
                        title="Edit name / role"
                        className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded transition-colors"
                      >
                        <User size={14} />
                      </button>
                      <button
                        onClick={() => setSetPassUser(u)}
                        title="Set password"
                        className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded transition-colors"
                      >
                        <KeyRound size={14} />
                      </button>
                      <button
                        onClick={() => toggleMut.mutate({ id: u.id, is_active: !u.is_active })}
                        title={u.is_active ? 'Deactivate' : 'Activate'}
                        className={`p-1.5 rounded transition-colors ${u.is_active ? 'text-slate-400 hover:text-orange-500' : 'text-slate-400 hover:text-green-500'}`}
                      >
                        {u.is_active ? <ToggleRight size={14} /> : <ToggleLeft size={14} />}
                      </button>
                      <button
                        onClick={() => {
                          if (confirm(`Delete user "${u.full_name}"? This cannot be undone.`)) {
                            deleteMut.mutate(u.id)
                          }
                        }}
                        title="Delete user"
                        className="p-1.5 text-slate-400 hover:text-red-500 rounded transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {createOpen && <CreateUserModal onClose={() => setCreateOpen(false)} />}
      {editUser && <EditUserModal user={editUser} onClose={() => setEditUser(null)} />}
      {setPassUser && <SetPasswordModal user={setPassUser} onClose={() => setSetPassUser(null)} />}
    </>
  )
}

/* ── My Account Tab ─────────────────────────────────────────── */

type PasswordForm = { current_password: string; new_password: string; confirm_password: string }

function AccountTab() {
  const { user } = useAuth()
  const [success, setSuccess] = useState(false)

  const { register, handleSubmit, watch, reset, formState: { errors, isSubmitting } } = useForm<PasswordForm>()

  const changeMut = useMutation({
    mutationFn: ({ current_password, new_password }: PasswordForm) =>
      adminApi.changePassword(current_password, new_password),
    onSuccess: () => { setSuccess(true); reset() },
  })

  return (
    <div className="max-w-md space-y-6">
      {/* Profile info */}
      <div className="neu-card p-5">
        <h2 className="section-title mb-4">Profile</h2>
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center">
            <User size={24} className="text-indigo-600 dark:text-indigo-400" />
          </div>
          <div>
            <p className="font-semibold text-slate-900 dark:text-slate-100">{user?.full_name}</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">{user?.email}</p>
            <RoleBadge role={user?.role ?? ''} />
          </div>
        </div>
      </div>

      {/* Change password */}
      <div className="neu-card p-5">
        <h2 className="section-title mb-4 flex items-center gap-2">
          <KeyRound size={15} />
          Change Password
        </h2>

        {success && (
          <div className="mb-4 text-xs text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/20 rounded-lg px-3 py-2 flex items-center gap-2">
            <ShieldCheck size={14} />
            Password updated successfully.
          </div>
        )}

        <form onSubmit={handleSubmit(data => { setSuccess(false); changeMut.mutate(data) })} className="space-y-4">
          <div>
            <label className="form-label">Current Password <span className="text-red-500">*</span></label>
            <input {...register('current_password', { required: 'Required' })} type="password" className="neu-input" />
            {errors.current_password && <p className="text-xs text-red-500 mt-1">{errors.current_password.message}</p>}
          </div>
          <div>
            <label className="form-label">New Password <span className="text-red-500">*</span></label>
            <input
              {...register('new_password', { required: 'Required', minLength: { value: 8, message: 'Min 8 characters' } })}
              type="password"
              className="neu-input"
            />
            {errors.new_password && <p className="text-xs text-red-500 mt-1">{errors.new_password.message}</p>}
          </div>
          <div>
            <label className="form-label">Confirm New Password <span className="text-red-500">*</span></label>
            <input
              {...register('confirm_password', {
                required: 'Required',
                validate: v => v === watch('new_password') || 'Passwords do not match',
              })}
              type="password"
              className="neu-input"
            />
            {errors.confirm_password && <p className="text-xs text-red-500 mt-1">{errors.confirm_password.message}</p>}
          </div>

          {changeMut.error && (
            <p className="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
              {(changeMut.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Failed to change password'}
            </p>
          )}

          <button type="submit" disabled={isSubmitting || changeMut.isPending} className="btn-primary">
            {changeMut.isPending ? 'Updating…' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  )
}

/* ── Main page ──────────────────────────────────────────────── */

export default function AdminPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [tab, setTab] = useState<Tab>(isAdmin ? 'users' : 'account')

  return (
    <div>
      <div className="mb-6">
        <h1 className="page-title">Admin Console</h1>
        <p className="page-subtitle">
          {isAdmin ? 'Manage users and account settings' : 'Account settings'}
        </p>
      </div>

      {/* Tab switcher */}
      {isAdmin && (
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab('users')}
            className={tab === 'users' ? 'neu-pill-active' : 'neu-pill'}
          >
            Users
          </button>
          <button
            onClick={() => setTab('account')}
            className={tab === 'account' ? 'neu-pill-active' : 'neu-pill'}
          >
            My Account
          </button>
        </div>
      )}

      {tab === 'users' && isAdmin ? <UsersTab /> : <AccountTab />}
    </div>
  )
}
