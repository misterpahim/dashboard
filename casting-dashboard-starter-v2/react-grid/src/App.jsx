import React, { useEffect, useMemo, useState } from 'react'
import GridLayout from 'react-grid-layout'
import ReactECharts from 'echarts-for-react'
import axios from 'axios'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const defaultLayout = [
  { i: 'oee_trend', x: 0, y: 0, w: 6, h: 6 },
  { i: 'dt_tonnage', x: 6, y: 0, w: 6, h: 6 },
  { i: 'good_parts', x: 0, y: 6, w: 6, h: 6 },
  { i: 'dt_partdie', x: 6, y: 6, w: 6, h: 6 },
]

function loadLayout() {
  try { return JSON.parse(localStorage.getItem('layout')) || defaultLayout } catch { return defaultLayout }
}
function saveLayout(layout) { localStorage.setItem('layout', JSON.stringify(layout)) }

export default function App() {
  const [layout, setLayout] = useState(loadLayout())
  const [oeeSeries, setOeeSeries] = useState([])

  useEffect(() => {
    const today = new Date()
    const from = new Date(Date.now() - 30*24*3600*1000)
    const fmt = (d) => d.toISOString().slice(0,10)
    axios.get(`${API_BASE}/kpi/efficiency`, { params: { date_from: fmt(from), date_to: fmt(today) } })
      .then(res => {
        const rows = res.data || []
        const map = new Map()
        rows.forEach(r => {
          const d = r.report_date
          const v = r.metric_value*100
          map.set(d, (map.get(d)||[]).concat([v]))
        })
        const series = Array.from(map.entries())
          .map(([d, arr]) => ({ date: d, value: arr.reduce((a,b)=>a+b,0)/arr.length }))
          .sort((a,b)=> a.date.localeCompare(b.date))
        setOeeSeries(series)
      }).catch(()=>{})
  }, [])

  const oeeOption = useMemo(() => ({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: oeeSeries.map(x=>x.date) },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{ type: 'line', data: oeeSeries.map(x=>x.value), smooth: true }]
  }), [oeeSeries])

  return (
    <div style={{height:'100%', padding: 8, boxSizing:'border-box'}}>
      <h2>Asakai Drag-and-Drop Dashboard</h2>
      <p style={{marginTop:-10}}>Drag corners to resize. Drag title bars to move. Layout is saved to your browser automatically.</p>
      <button onClick={() => { setLayout(defaultLayout); saveLayout(defaultLayout) }}>Reset layout</button>
      <GridLayout
        className="layout"
        layout={layout}
        onLayoutChange={l => { setLayout(l); saveLayout(l) }}
        cols={12}
        rowHeight={30}
        width={window.innerWidth - 32}
        draggableHandle=".card-title"
      >
        <div key="oee_trend" className="card"><div className="card-title">Daily OEE Trend</div><ReactECharts option={oeeOption} style={{height:'100%'}} /></div>
        <div key="dt_tonnage" className="card"><div className="card-title">Downtime by DCM Tonnage</div><Placeholder /></div>
        <div key="good_parts" className="card"><div className="card-title">Total Good Parts by Part & Die</div><Placeholder /></div>
        <div key="dt_partdie" className="card"><div className="card-title">Downtime by Part & Die</div><Placeholder /></div>
      </GridLayout>
      <style>{`
        .card { background:#fff; border:1px solid #ddd; border-radius:12px; box-shadow: 0 1px 4px rgba(0,0,0,.06); overflow:hidden; display:flex; flex-direction:column; }
        .card-title { cursor:move; padding:10px 12px; font-weight:600; border-bottom:1px solid #eee; background:#fafafa; }
        .react-grid-item { transition: none; }
      `}</style>
    </div>
  )
}

function Placeholder() {
  return <div style={{flex:1, display:'flex', alignItems:'center', justifyContent:'center', color:'#888'}}>Wire up data to show stacked bars + OEE line.</div>
}
