// Test script para verificar la API
const axios = require('axios');

async function testAPI() {
    try {
        console.log('Probando backend...');
        const response = await axios.get('http://localhost:8000/');
        console.log('✅ Backend funcionando:', response.data);
        
        console.log('Probando login...');
        const loginResponse = await axios.post('http://localhost:8000/auth/login', {
            username: 'admin',
            password: 'admin123'
        });
        console.log('✅ Login funcionando:', loginResponse.data);
        
        const token = loginResponse.data.access_token;
        
        console.log('Probando productos...');
        const productosResponse = await axios.get('http://localhost:8000/productos/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log('✅ Productos funcionando:', productosResponse.data.length, 'productos');
        
        console.log('Probando clientes...');
        const clientesResponse = await axios.get('http://localhost:8000/clientes', {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log('✅ Clientes funcionando:', clientesResponse.data.items.length, 'clientes');
        
        console.log('Probando proveedores...');
        const proveedoresResponse = await axios.get('http://localhost:8000/proveedores', {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log('✅ Proveedores funcionando:', proveedoresResponse.data.items.length, 'proveedores');
        
        console.log('Probando ventas...');
        const ventasResponse = await axios.get('http://localhost:8000/ventas/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log('✅ Ventas funcionando:', ventasResponse.data.length, 'ventas');
        
        console.log('Probando compras...');
        const comprasResponse = await axios.get('http://localhost:8000/compras/1', {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log('✅ Compras funcionando:', comprasResponse.data);
        
        console.log('\n🎉 TODAS LAS PRUEBAS PASARON CORRECTAMENTE!');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Data:', error.response.data);
        }
    }
}

testAPI();




