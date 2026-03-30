import React, { useEffect, useState } from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { createUser, deleteUser, getUsers, updateUser } from '@/services/api';

const emptyForm = {
  username: '',
  password: '',
  is_active: true,
};

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    setLoading(true);
    setError('');
    try {
      const response = await getUsers();
      setUsers(response.data || []);
    } catch (loadError) {
      setError(loadError.message || '加载用户失败');
    } finally {
      setLoading(false);
    }
  }

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setOpen(true);
  }

  function openEdit(user) {
    setEditing(user);
    setForm({
      username: user.username,
      password: '',
      is_active: user.is_active,
    });
    setOpen(true);
  }

  async function handleSubmit() {
    if (!form.username.trim()) {
      setError('请输入用户名');
      return;
    }
    if (!editing && !form.password.trim()) {
      setError('请输入密码');
      return;
    }
    if (form.password && form.password.length < 6) {
      setError('密码至少6个字符');
      return;
    }

    setSaving(true);
    setError('');
    try {
      if (editing) {
        const payload = {
          username: form.username,
          is_active: form.is_active,
        };
        if (form.password) {
          payload.password = form.password;
        }
        await updateUser(editing.id, payload);
        setSuccess('用户更新成功');
      } else {
        await createUser({
          username: form.username,
          password: form.password,
        });
        setSuccess('用户创建成功');
      }
      setOpen(false);
      await loadUsers();
      setTimeout(() => setSuccess(''), 3000);
    } catch (submitError) {
      setError(submitError.message || '保存用户失败');
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleUser(user) {
    try {
      await updateUser(user.id, {
        username: user.username,
        is_active: !user.is_active,
      });
      setSuccess(`已${user.is_active ? '禁用' : '启用'}用户 ${user.username}`);
      await loadUsers();
      setTimeout(() => setSuccess(''), 3000);
    } catch (toggleError) {
      setError(toggleError.message || '更新用户状态失败');
    }
  }

  async function handleDeleteUser(user) {
    if (!window.confirm(`确认删除用户 ${user.username}？此操作不可恢复`)) {
      return;
    }

    try {
      await deleteUser(user.id);
      setSuccess(`已删除用户 ${user.username}`);
      await loadUsers();
      setTimeout(() => setSuccess(''), 3000);
    } catch (deleteError) {
      setError(deleteError.message || '删除用户失败');
    }
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {success && (
        <Alert className="border-green-200 bg-green-50">
          <AlertDescription className="text-green-700">{success}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <div>
              <CardTitle>用户管理</CardTitle>
              <CardDescription>管理员可新增、修改、禁用和删除用户。</CardDescription>
            </div>
            <Button onClick={openCreate}>新增用户</Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="py-8 text-center text-sm text-slate-500">加载中...</div>
          ) : users.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-500">暂无用户</div>
          ) : (
            <div className="space-y-3">
              {users.map((user) => (
                <div key={user.id} className="flex items-center justify-between rounded-lg border p-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900">{user.username}</span>
                      {user.username === 'admin' && <Badge variant="outline">管理员</Badge>}
                      <Badge className={user.is_active ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-700'}>
                        {user.is_active ? '启用' : '禁用'}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-500">
                      创建时间: {user.created_at ? new Date(user.created_at).toLocaleString('zh-CN') : '--'}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => openEdit(user)}>
                      编辑
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleToggleUser(user)}>
                      {user.is_active ? '禁用' : '启用'}
                    </Button>
                    {user.username !== 'admin' && (
                      <Button variant="destructive" size="sm" onClick={() => handleDeleteUser(user)}>
                        删除
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? '编辑用户' : '新增用户'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="username">用户名</Label>
              <Input
                id="username"
                value={form.username}
                onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
                placeholder="请输入用户名"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">{editing ? '新密码（不填则不修改）' : '密码'}</Label>
              <Input
                id="password"
                type="password"
                value={form.password}
                onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
                placeholder={editing ? '留空表示不修改密码' : '请输入密码'}
              />
            </div>
            {editing && (
              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(event) => setForm((prev) => ({ ...prev, is_active: event.target.checked }))}
                />
                <span>启用用户</span>
              </label>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSubmit} disabled={saving}>
              {saving ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
