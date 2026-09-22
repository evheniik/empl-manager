export default function ConfirmDialog({ open, message, loading, onConfirm, onCancel }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={loading ? undefined : onCancel}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label="Confirm delete"
        onClick={(e) => e.stopPropagation()}
      >
        <p>{message}</p>
        <div className="row">
          <button type="button" onClick={onConfirm} disabled={loading} autoFocus>
            {loading ? 'Deleting...' : 'Delete'}
          </button>
          <button type="button" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}