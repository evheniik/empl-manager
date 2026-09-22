import { useState } from 'react';
import { useAuth } from '../AuthContext.jsx';
import { api } from '../api.js';
import ConfirmDialog from '../components/ConfirmDialog.jsx';
import { EMAIL_RE } from '../constants.js';
import { useCompanies, useCrud } from '../hooks/useCrud.js';

const emptyForm = {
  first_name: '',
  last_name: '',
  email: '',
  position: '',
  company_id: '',
};

function validate(form) {
  if (!form.first_name.trim()) return 'First name is required.';
  if (!form.last_name.trim()) return 'Last name is required.';
  if (!form.email.trim()) return 'Email is required.';
  if (!EMAIL_RE.test(form.email.trim())) return 'Email is not valid.';
  if (!form.position.trim()) return 'Position is required.';
  if (!form.company_id) return 'Company is required.';
  return '';
}

export default function EmployeesPage() {
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
    fetchItems: () => api.listEmployees({ companyId: filterCompany || undefined }),
    createItem: api.createEmployee,
    updateItem: api.updateEmployee,
    deleteItem: api.deleteEmployee,
    emptyForm,
    toPayload: (f) => ({
      first_name: f.first_name.trim(),
      last_name: f.last_name.trim(),
      email: f.email.trim(),
      position: f.position.trim(),
      company_id: f.company_id,
    }),
    validate,
    confirmMessage: () => 'Delete this employee?',
    dependencies: [filterCompany],
  });

  function companyName(id) {
    return companies.find((c) => c.id === id)?.name ?? id;
  }

  return (
    <div>
      <h2>Employees</h2>
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
          <h3>{editingId ? 'Edit employee' : 'Create employee'}</h3>
          <label>
            First name
            <input
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
            />
          </label>
          <label>
            Last name
            <input
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
            />
          </label>
          <label>
            Email
            <input
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </label>
          <label>
            Position
            <input
              value={form.position}
              onChange={(e) => setForm({ ...form, position: e.target.value })}
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
              <th>First name</th>
              <th>Last name</th>
              <th>Email</th>
              <th>Position</th>
              <th>Company</th>
              {isAuthenticated && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {items.map((emp) => (
              <tr key={emp.id}>
                <td>{emp.first_name}</td>
                <td>{emp.last_name}</td>
                <td>{emp.email}</td>
                <td>{emp.position}</td>
                <td>{companyName(emp.company_id)}</td>
                {isAuthenticated && (
                  <td>
                    <div className="row">
                      <button type="button" onClick={() => startEdit(emp)}>
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => requestDelete(emp)}
                        disabled={deletingId === emp.id}
                      >
                        {deletingId === emp.id ? 'Deleting...' : 'Delete'}
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
        message="Delete this employee?"
        loading={Boolean(confirmItem) && deletingId === confirmItem.id}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}