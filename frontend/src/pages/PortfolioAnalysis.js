import React, { useState, useEffect } from 'react';
import apiClient from '../api';

const PortfolioAnalysis = () => {
  const [availableStocks, setAvailableStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  console.log('PortfolioAnalysis component rendering');

  useEffect(() => {
    console.log('PortfolioAnalysis useEffect running');
    fetchAvailableStocks();
  }, []);

  const fetchAvailableStocks = async () => {
    try {
      console.log('Fetching available stocks...');
      const response = await apiClient.get('/portfolio/available-stocks');
      console.log('Available stocks response:', response.data);
      setAvailableStocks(response.data);
    } catch (error) {
      console.error('Error fetching available stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  console.log('Rendering PortfolioAnalysis with availableStocks:', availableStocks.length);

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f9fafb',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: '18px',
        color: '#374151'
      }}>
        Loading Portfolio Analysis...
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '16px' }}>
            AI-Powered Portfolio Analysis
          </h1>
          <p style={{ fontSize: '1.25rem', color: '#6b7280' }}>
            Build your portfolio and get comprehensive risk assessment and recommendations
          </p>
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', padding: '24px' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>
            Available Stocks ({availableStocks.length})
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
            {availableStocks.map(stock => (
              <div key={stock.symbol} style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '8px', 
                padding: '16px',
                backgroundColor: '#f9fafb'
              }}>
                <div style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                  {stock.symbol}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                  {stock.name}
                </div>
                <div style={{ 
                  fontSize: '0.75rem', 
                  backgroundColor: '#dbeafe', 
                  color: '#1e40af', 
                  padding: '4px 8px', 
                  borderRadius: '4px',
                  display: 'inline-block'
                }}>
                  {stock.sector}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioAnalysis; 