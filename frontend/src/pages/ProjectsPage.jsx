import { useState } from 'react';
import { useAuth } from '../AuthContext.jsx';
import { api } from '../api.js';
import ConfirmDialog from '../components/ConfirmDialog.jsx';
import { useCompanies, useCrud } from '../hooks/useCrud.js';

const emptyForm = { name: '', description: '', company_id: '' };

function validate(form) {
  if (!form.name.trim()) return 'Name is required.';
  if (!form.company_id) return 'Company is required.';
  return '';
}

export default function ProjectsPage() {
  const { isAuthenticated } = useAuth();
  const companies = useCompanies();
  const [filterCompany, setFilterCompany] = useState('');
  const {
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
  } = useCrud({
    fetchItems: () => api.listProjects({ companyId: filterCompany || undefined }),
    createItem: api.createProject,
    updateItem: api.updateProject,
    deleteItem: api.deleteProject,
    emptyForm,
    toPayload: (f) => ({
      name: f.name.trim(),
      description: f.description.trim() || null,
      company_id: f.company_id,
    }),
    validate,
    confirmMessage: () => 'Delete this project?',
    dependencies: [filterCompany],
  });

  function companyName(id) {
    return companies.find((c) => c.id === id)?.name ?? id;
  }

  return (
    <div>
      <h2>Projects</h2>
      {error && <p className="error">{error}</p>}
      <div className="row">
        <label>
          Filter by company
          <select value={filterCompany} onChange={(e) => setFilterCompany(e.target.value)}>
            <option value="">All</option>
            {companies.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {isAuthenticated && (
        <form onSubmit={handleSubmit} className="form card" noValidate>
          <h3>{editingId ? 'Edit project' : 'Create project'}</h3>
          <label>
            Name
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </label>
          <label>
            Description
            <input
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </label>
          <label>
            Company
            <select
              value={form.company_id}
              onChange={(e) => setForm({ ...form, company_id: e.target.value })}
            >
              <option value="">Select company</option>
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <div className="row">
            <button type="submit" disabled={saving}>
              {saving ? 'Saving...' : editingId ? 'Save' : 'Create'}
            </button>
            {editingId && (
              <button type="button" onClick={cancelEdit} disabled={saving}>
                Cancel
              </button>
            )}
          </div>
        </form>
      )}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Company</th>
              {isAuthenticated && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>{p.description ?? ''}</td>
                <td>{companyName(p.company_id)}</td>
                {isAuthenticated && (
                  <td>
                    <div className="row">
                      <button type="button" onClick={() => startEdit(p)}>
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => requestDelete(p)}
                        disabled={deletingId === p.id}
                      >
                        {deletingId === p.id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <ConfirmDialog
        open={Boolean(confirmItem)}
        message="Delete this project?"
        loading={Boolean(confirmItem) && deletingId === confirmItem.id}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}