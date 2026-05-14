import React, { useState, useRef, useEffect } from 'react';

const PdfViewer = ({ pdfUrl, onReset, plantillas = [] }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const fullPdfUrl = pdfUrl ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${pdfUrl}` : null;

  const handleLoad = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setError('Error al cargar el PDF');
  };

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleDescargar = (file) => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    window.open(`${base}/static/plantillas/${file}`, '_blank');
    setDropdownOpen(false);
  };

  return (
    <div className="h-full flex flex-col bg-oracle-dark">
      {/* Header */}
      <div className="p-4 border-b border-oracle-border flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-oracle-text flex items-center gap-2">
            <svg className="w-5 h-5 text-oracle-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Reporte
          </h2>
          <p className="text-xs text-oracle-muted mt-1">Documento de análisis generado</p>

          {/* Botón Descargar Plantillas con dropdown */}
          <div className="relative mt-2" ref={dropdownRef}>
            <button
              type="button"
              onClick={() => setDropdownOpen(prev => !prev)}
              className="btn-secondary flex items-center gap-2 text-xs px-3 py-1.5"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Descargar Plantillas
              <svg
                className={`w-3 h-3 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`}
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {dropdownOpen && (
              <div className="absolute left-0 top-full mt-1 z-50 bg-oracle-surface border border-oracle-border rounded-lg shadow-lg min-w-max">
                {plantillas.length === 0 ? (
                  <div className="px-4 py-2 text-sm text-oracle-muted">No hay plantillas</div>
                ) : (
                  plantillas.map((filename) => (
                    <button
                      key={filename}
                      type="button"
                      onClick={() => handleDescargar(filename)}
                      className="w-full text-left px-4 py-2 text-sm text-oracle-text hover:bg-oracle-border transition-colors duration-150 first:rounded-t-lg last:rounded-b-lg flex items-center gap-2"
                    >
                      <svg className="w-4 h-4 text-oracle-accent shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      {filename}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* Abrir en nueva pestaña */}
        {pdfUrl && (
          <a
            href={fullPdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary flex items-center gap-2 text-sm self-start"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Abrir
          </a>
        )}
      </div>

      {/* Cuerpo principal */}
      <div className="flex-1 overflow-hidden bg-oracle-surface">
        {pdfUrl ? (
          <div className="h-full flex flex-col">
            {isLoading && (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <svg className="w-12 h-12 text-oracle-accent animate-spin mx-auto" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p className="text-oracle-muted mt-2">Cargando PDF...</p>
                </div>
              </div>
            )}

            {error && (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <svg className="w-12 h-12 text-oracle-error mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-oracle-error mt-2">{error}</p>
                </div>
              </div>
            )}

            <iframe
              src={fullPdfUrl}
              className="flex-1 w-full border-0"
              style={{ display: isLoading || error ? 'none' : 'block' }}
              onLoad={handleLoad}
              onError={handleError}
              title="PDF Viewer"
            />
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-8">
            <div className="w-20 h-20 rounded-full bg-oracle-surface border border-oracle-border flex items-center justify-center mb-4">
              <svg className="w-10 h-10 text-oracle-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-oracle-text font-medium">Sin reporte disponible</h3>
            <p className="text-oracle-muted text-sm mt-2 max-w-xs">
              El reporte PDF se generará automáticamente después de que los agentes completen el análisis
            </p>
          </div>
        )}
      </div>

      {/* Footer con botón Nueva Consulta */}
      {pdfUrl && (
        <div className="p-4 border-t border-oracle-border">
          <button
            onClick={onReset}
            className="btn-secondary w-full flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Nueva Consulta
          </button>
        </div>
      )}
    </div>
  );
};

export default PdfViewer;