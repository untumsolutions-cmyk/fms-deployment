import React from 'react';
export default function Invoices(){ const openPDF=()=>{ window.open('http://localhost:8000/export/invoice/1','_blank'); }; return (<div><h2>Invoices</h2><button onClick={openPDF}>Download Invoice #1 (PDF)</button></div>); }
