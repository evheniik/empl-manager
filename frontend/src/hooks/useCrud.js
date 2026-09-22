import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api.js';

export function useCrud({
  fetchItems,
  createItem,
  updateItem,
  deleteItem,
  emptyForm,
  toPayload = (form) => form,
  validate,
  confirmMessage = () => 'Delete this item?',
  dependencies = [],
}) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [confirmItem, setConfirmItem] = useState(null);
  const depsRef = useRef(dependencies);
  depsRef.current = dependencies;

  const load = useCallback(async (showLoader = true) => {
    if (showLoader) setLoading(true);
    setError('');
    try {
      setItems(await fetchItems());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchItems]);

  const refresh = useCallback(() => load(false), [load]);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, depsRef.current);

  function startEdit(item) {
    setEditingId(item.id);
    const next = {};
    for (const key of Object.keys(emptyForm)) {
      next[key] = item[key] ?? '';
    }
    setForm(next);
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const validationError = validate ? validate(form) : '';
    if (validationError) {
      setError(validationError);
      return;
    }
    setError('');
    setSaving(true);
    try {
      const payload = toPayload(form);
      if (editingId) {
        await updateItem(editingId, payload);
      } else {
        await createItem(payload);
      }
      cancelEdit();
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  function requestDelete(item) {
    setConfirmItem(item);
  }

  function cancelDelete() {
    setConfirmItem(null);
  }

  async function confirmDelete() {
    if (!confirmItem) return;
    setDeletingId(confirmItem.id);
    setError('');
    try {
      await deleteItem(confirmItem.id);
      setConfirmItem(null);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  }

  return {
    items,
    loading,
    saving,
    deletingId,
    error,
    form,
    setForm,
    editingId,
    startEdit,
    cancelEdit,
    handleSubmit,
    requestDelete,
    cancelDelete,
    confirmDelete,
    confirmItem,
    confirmMessage,
  };
}

export function useCompanies() {
  const [companies, setCompanies] = useState([]);

  useEffect(() => {
    api.listCompanies().then(setCompanies).catch(() => {});
  }, []);

  return companies;
}