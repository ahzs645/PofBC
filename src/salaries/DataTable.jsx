// Records as a table, built on TanStack Table (sorting, filtering) and TanStack Virtual (only the rows
// in view are drawn, so tens of thousands scroll as one list). Every column sorts from its header;
// a text column filters by the words typed under it, a money column by a lowest amount. The table
// scrolls inside its own box, down and across, with the header and the first column kept in view.

import { useMemo, useRef, useState } from 'react'
import { flexRender, getCoreRowModel, getFilteredRowModel, getSortedRowModel, useReactTable } from '@tanstack/react-table'
import { useVirtualizer } from '@tanstack/react-virtual'

const folded = (value) => String(value ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

/** Every word typed appears somewhere in the cell. */
const wordsFilter = (row, id, value) => {
  const text = folded(row.getValue(id))
  return folded(value).split(/\s+/).filter(Boolean).every((word) => text.includes(word))
}
/** At least the amount typed. */
const minimumFilter = (row, id, value) => {
  const least = Number(String(value).replace(/[^0-9.-]/g, ''))
  return !Number.isFinite(least) || (row.getValue(id) ?? -Infinity) >= least
}

/**
 * @param {object} props
 * @param {Array} props.data
 * @param {Array} props.columns  TanStack column definitions; `meta.kind` 'money' or 'number'
 *                               right-aligns the column and filters it by a lowest amount, `meta.filter: false` leaves
 *                               a column without a filter.
 * @param {Array} [props.sorting] The order the table opens in.
 * @param {string} props.label    What the table holds, for screen readers.
 */
export const DataTable = ({ data, columns, sorting: initialSorting = [], label, rowHeight = 44 }) => {
  const [sorting, setSorting] = useState(initialSorting)
  const [columnFilters, setColumnFilters] = useState([])
  const prepared = useMemo(() => columns.map((column) => ({
    ...column,
    filterFn: column.filterFn ?? (['money', 'number'].includes(column.meta?.kind) ? minimumFilter : wordsFilter),
    enableColumnFilter: column.meta?.filter !== false
  })), [columns])
  const table = useReactTable({
    data, columns: prepared, state: { sorting, columnFilters }, onSortingChange: setSorting, onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(), getSortedRowModel: getSortedRowModel(), getFilteredRowModel: getFilteredRowModel()
  })
  const { rows } = table.getRowModel()
  const box = useRef(null)
  const virtual = useVirtualizer({ count: rows.length, getScrollElement: () => box.current, estimateSize: () => rowHeight, overscan: 12 })
  const items = virtual.getVirtualItems()
  const before = items.length ? items[0].start : 0
  const after = items.length ? virtual.getTotalSize() - items.at(-1).end : 0
  const span = table.getVisibleLeafColumns().length

  return (
    <div className="salaries-datatable">
      <p className="salaries__meta salaries-datatable__count" role="status">
        {rows.length.toLocaleString('en-CA')} of {data.length.toLocaleString('en-CA')} {data.length === 1 ? 'row' : 'rows'}
        {columnFilters.length > 0 && <> · <button type="button" className="salaries__link" onClick={() => setColumnFilters([])}>Clear column filters</button></>}
      </p>
      <div ref={box} className="salaries-table salaries-table--scroll" role="region" aria-label={label} tabIndex={0}>
        <table>
          <thead>
            {table.getHeaderGroups().map((group) => (
              <tr key={group.id}>
                {group.headers.map((header) => {
                  const sorted = header.column.getIsSorted()
                  return (
                    <th key={header.id} scope="col" data-kind={header.column.columnDef.meta?.kind} aria-sort={sorted ? (sorted === 'asc' ? 'ascending' : 'descending') : 'none'}>
                      <button type="button" className="salaries-datatable__sort" onClick={header.column.getToggleSortingHandler()}>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        <span aria-hidden="true">{sorted === 'asc' ? ' ↑' : sorted === 'desc' ? ' ↓' : ''}</span>
                      </button>
                      {header.column.getCanFilter() && (
                        <input
                          className="salaries-datatable__filter"
                          type={['money', 'number'].includes(header.column.columnDef.meta?.kind) ? 'number' : 'search'}
                          inputMode={['money', 'number'].includes(header.column.columnDef.meta?.kind) ? 'numeric' : undefined}
                          placeholder={['money', 'number'].includes(header.column.columnDef.meta?.kind) ? 'At least' : 'Filter'}
                          aria-label={`Filter ${typeof header.column.columnDef.header === 'string' ? header.column.columnDef.header : header.id}`}
                          value={header.column.getFilterValue() ?? ''}
                          onChange={(event) => header.column.setFilterValue(event.target.value || undefined)}
                        />
                      )}
                    </th>
                  )
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {before > 0 && <tr aria-hidden="true"><td colSpan={span} style={{ height: before, padding: 0, border: 0 }} /></tr>}
            {items.map((item) => {
              const row = rows[item.index]
              return (
                <tr key={row.id} data-index={item.index} ref={virtual.measureElement}>
                  {row.getVisibleCells().map((cell, at) => {
                    const Cell = at === 0 ? 'th' : 'td'
                    return <Cell key={cell.id} scope={at === 0 ? 'row' : undefined} data-kind={cell.column.columnDef.meta?.kind}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</Cell>
                  })}
                </tr>
              )
            })}
            {after > 0 && <tr aria-hidden="true"><td colSpan={span} style={{ height: after, padding: 0, border: 0 }} /></tr>}
          </tbody>
        </table>
        {!rows.length && <p className="salaries__hint salaries-datatable__empty">No rows match these filters.</p>}
      </div>
    </div>
  )
}
