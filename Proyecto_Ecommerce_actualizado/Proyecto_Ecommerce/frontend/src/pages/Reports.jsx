import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, ShoppingBag, Package } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Reports.css';

const API_BASE = 'http://127.0.0.1:8000/api';

const Reports = () => {
  const { authFetch } = useAuth();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const loadReport = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.set('date_from', dateFrom);
      if (dateTo) params.set('date_to', dateTo);
      const res = await authFetch(`${API_BASE}/reports/sales/?${params.toString()}`);
      if (!res.ok) throw new Error('No se pudo cargar el reporte de ventas');
      const data = await res.json();
      setReport(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const maxDayRevenue = report?.sales_by_day?.length
    ? Math.max(...report.sales_by_day.map((d) => Number(d.revenue)))
    : 0;

  return (
    <div className="container reports-page">
      <div className="reports-header">
        <BarChart3 size={26} />
        <h1>Reporte de Ventas</h1>
      </div>

      <div className="reports-filters glass-panel">
        <label>
          Desde
          <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
        </label>
        <label>
          Hasta
          <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
        </label>
        <button className="btn-primary" onClick={loadReport}>Filtrar</button>
      </div>

      {error && <p className="reports-error">{error}</p>}
      {loading && <p>Cargando reporte...</p>}

      {!loading && report && (
        <>
          <div className="reports-summary">
            <div className="summary-card glass-panel">
              <TrendingUp size={22} />
              <div>
                <span className="summary-value">Gs. {Number(report.total_revenue).toLocaleString('es-PY')}</span>
                <span className="summary-label">Ingresos totales</span>
              </div>
            </div>
            <div className="summary-card glass-panel">
              <ShoppingBag size={22} />
              <div>
                <span className="summary-value">{report.total_orders}</span>
                <span className="summary-label">Pedidos pagados</span>
              </div>
            </div>
          </div>

          <div className="reports-grid">
            <div className="reports-panel glass-panel">
              <h2>Ventas por día</h2>
              {report.sales_by_day.length === 0 ? (
                <p className="no-data">Sin ventas registradas en el período.</p>
              ) : (
                <div className="bars-chart">
                  {report.sales_by_day.map((day) => (
                    <div key={day.day} className="bar-row">
                      <span className="bar-label">{day.day}</span>
                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{ width: `${maxDayRevenue ? (Number(day.revenue) / maxDayRevenue) * 100 : 0}%` }}
                        />
                      </div>
                      <span className="bar-value">Gs. {Number(day.revenue).toLocaleString('es-PY')}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="reports-panel glass-panel">
              <h2><Package size={18} /> Productos más vendidos</h2>
              {report.top_products.length === 0 ? (
                <p className="no-data">Sin datos todavía.</p>
              ) : (
                <table className="products-table">
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Unidades</th>
                      <th>Ingresos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.top_products.map((p) => (
                      <tr key={p.product_name}>
                        <td>{p.product_name}</td>
                        <td>{p.units_sold}</td>
                        <td>Gs. {Number(p.revenue).toLocaleString('es-PY')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Reports;
