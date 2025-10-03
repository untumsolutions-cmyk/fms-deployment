import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Logo from './pages/Logo';
import Invoices from './pages/Invoices';
export default function App(){
  return (<BrowserRouter><div style={{padding:20}}><h1>FMS</h1><nav><Link to='/logo'>Upload Logo</Link> | <Link to='/invoices'>Invoices</Link></nav><Routes><Route path='/logo' element={<Logo/>} /><Route path='/invoices' element={<Invoices/>} /><Route path='/' element={<div>Welcome</div>} /></Routes></div></BrowserRouter>);
}
