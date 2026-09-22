import { useAuth } from '../AuthContext.jsx';
import { api } from '../api.js';
import ConfirmDialog from '../components/ConfirmDialog.jsx';
import { useCrud } from '../hooks/useCrud.js';

const emptyForm = { name: '', description: '', website: '' };

function validate(form) {
  if (!form.name.trim()) return 'Name is required.';
  if (
    form.website &&
    !/^https?:\/\/\S+\.\S+$/.test(form.website.trim())
  ) {
    return 'Website must be a valid URL, e.g. https://example.com.';
  }
  return '';
}

export default function CompaniesPage() {
  const { isAuthenticated } = useAuth();
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
    confirmMessage,
  } = useCrud({
    fetchItems: () => api.listCompanies(),
    createItem: api.createCompany,
    updateItem: api.updateCompany,
    deleteItem: api.deleteCompany,
    emptyForm,
    toPayload: (f) => ({
      name: f.name.trim(),
      description: f.description.trim() || null,
      website: f.website.trim() || null,
    }),
    validate,
    confirmMessage: () => 'Delete this company?',
  });

  return (
    <div>
      <h2>Companies</h2>
      {error && <p className="error">{error}</p>}
      {isAuthenticated && (
        <form onSubmit={handleSubmit} className="form card" noValidate>
          <h3>{editingId ? 'Edit company' : 'Create company'}</h3>
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
            Website
            <input
              value={form.website}
              onChange={(e) => setForm({ ...form, website: e.target.value })}
              placeholder="https://example.com"
            />
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
              <th>Website</th>
              {isAuthenticated && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.description ?? ''}</td>
                <td>{c.website ?? ''}</td>
                {isAuthenticated && (
                  <td>
                    <div className="row">
                      <button type="button" onClick={() => startEdit(c)}>
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => requestDelete(c)}
                        disabled={deletingId === c.id}
                      >
                        {deletingId === c.id ? 'Deleting...' : 'Delete'}
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
        message={confirmMessage(confirmItem)}
        loading={Boolean(confirmItem) && deletingId === confirmItem.id}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}