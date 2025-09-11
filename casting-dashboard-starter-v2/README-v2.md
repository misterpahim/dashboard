# Casting Dashboard V2

## Tools
- `tools/discover_cells.py` — scans numeric daily sheets for labels like OEE, downtime categories, and good parts, and prints likely value cell addresses. Use:
```
python tools/discover_cells.py "/path/to/your.xlsx" > candidates.json
```
Review the output and decide which addresses to fix in `metric_definitions` or your ingest mapping.

## React Drag-and-Drop Dashboard
Inside `react-grid/` is a Vite React app using `react-grid-layout` (drag/resize) and ECharts.
- `npm i`
- Set API base: `VITE_API_BASE=http://localhost:8000`
- `npm run dev` (open http://localhost:5173)

The OEE trend is wired; the other three cards are placeholders until you ingest those metrics.
