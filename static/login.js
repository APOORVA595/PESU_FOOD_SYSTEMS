// static/login.js

const LOGIN_API_URL = '/api/login'; // The route Ashrita needs to create

document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const userId = document.getElementById('user-id').value.trim().toUpperCase();
    const messageDiv = document.getElementById('login-message');
    
    messageDiv.classList.add('d-none'); // Hide previous message
    
    // 1. Send ID to the Integrator's backend API
    try {
        const response = await fetch(LOGIN_API_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId })
        });

        const result = await response.json();

        // 2. Handle the response and redirect based on the role determined by the backend
        if (response.ok && result.status === 'Success') {
            const role = result.role; // Backend must return the role ('Customer' or 'Admin')
            
            messageDiv.className = 'alert mt-3 alert-success';
            messageDiv.textContent = `Login successful as ${role}. Redirecting...`;
            
            // Redirect based on the role
            if (role === 'Customer') {
                // Phase 1 Ordering Page
                window.location.href = '/order-page'; 
            } else if (role === 'Admin') {
                // Phase 2 Admin Dashboard (Needs to be created later)
                window.location.href = '/admin-dashboard';
            }
        } else {
            // Login failed (ID not found in Customer OR Shop tables)
            messageDiv.className = 'alert mt-3 alert-danger';
            messageDiv.textContent = result.message || 'Invalid ID or network error.';
        }

    } catch (error) {
        console.error('Login failed:', error);
        messageDiv.className = 'alert mt-3 alert-danger';
        messageDiv.textContent = 'Network error. Could not connect to the server.';
    }
    
    messageDiv.classList.remove('d-none');
});