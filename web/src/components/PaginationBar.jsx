"use client";

export function PaginationBar({
  pageSize,
  onPageSizeChange,
  canPrev,
  canNext,
  onPrev,
  onNext,
}) {
  return (
    <div className="pager">
      <label className="pager-size">
        Page size
        <select
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
        >
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
        </select>
      </label>
      <div className="pager-btns">
        <button
          type="button"
          className="btn ghost"
          disabled={!canPrev}
          onClick={onPrev}
        >
          Prev
        </button>
        <button
          type="button"
          className="btn ghost"
          disabled={!canNext}
          onClick={onNext}
        >
          Next
        </button>
      </div>
    </div>
  );
}
