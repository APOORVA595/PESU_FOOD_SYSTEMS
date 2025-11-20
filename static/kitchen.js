// static/kitchen.js

// Function to use the toast notification defined in kitchen_dashboard.html
// This replaces all instances of alert()
function showToast(type, message) {
    const toast = document.createElement('div');
    // Use position-fixed to keep it on top of the screen
    toast.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3 shadow-lg`;
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    toast.style.borderRadius = '8px';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        toast.remove();
    }, 4000);
}


document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch of active orders when the page loads
    fetchActiveOrders();
    // Refresh orders every 10 seconds for a real-time feel
    // Use a variable to store the interval ID for cleanup
    const autoRefreshInterval = setInterval(fetchActiveOrders, 10000); 

    // Event delegation for "Mark Ready" buttons
    document.getElementById('order-queue-container').addEventListener('click', (event) => {
        if (event.target.classList.contains('btn-mark-ready')) {
            const orderId = event.target.dataset.orderId;
            const prepId = event.target.dataset.prepId;
            if (orderId && prepId) {
                markOrderAsReady(orderId, prepId, event.target);
            }
        }
    });

    // Clean up interval on page unload (Good practice)
    window.addEventListener('beforeunload', () => {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
    });
});

async function fetchActiveOrders() {
    const queueContainer = document.getElementById('order-queue-container');
    const placeholder = document.getElementById('order-queue-placeholder');
    
    // The placeholder serves as the initial "Loading" message and fallback "No Orders"
    placeholder.innerHTML = 'Loading active orders...';
    placeholder.classList.remove('d-none');
    queueContainer.innerHTML = ''; // Clear previous list

    try {
        const response = await fetch('/api/admin/active-orders'); 
        const orders = await response.json();

        if (!response.ok) {
             throw new Error(orders.message || 'Failed to fetch orders from server.');
        }

        if (orders.length === 0) {
            placeholder.textContent = 'No orders currently in preparation.';
            placeholder.classList.remove('d-none');
        } else {
            placeholder.classList.add('d-none'); // Hide placeholder if there are orders
            orders.forEach(order => {
                queueContainer.appendChild(createOrderCard(order));
            });
        }

    } catch (error) {
        console.error('Error fetching active orders:', error);
        placeholder.textContent = `Error loading orders: ${error.message}`;
        // Do not hide placeholder on error
    }
}

function createOrderCard(order) {
    const cardContainer = document.createElement('div');
    // Using col-md-4 for a nice three-column layout on desktop
    cardContainer.className = 'col-md-4 mb-4'; 
    
    // Determine card styling based on status
    const cardClass = order.status === 'Ready' 
        ? 'order-card-ready border-success' 
        : 'border-warning'; // Assuming "Preparing" is the default for a warning border

    const buttonDisabled = order.status === 'Ready' ? 'disabled' : '';
    const buttonText = order.status === 'Ready' ? 'Ready for Pickup' : 'Mark Ready (Trigger Notification)';

    // Format the time left
    const timeLeftHtml = order.time_left 
        ? `<span class="badge ${order.time_left === 'Overdue' ? 'bg-danger' : 'bg-primary'} text-white">${order.time_left} left</span>`
        : '';
        
    cardContainer.innerHTML = `
        <div class="card order-card shadow-sm h-100 ${cardClass}">
            <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title text-danger fw-bold">Order #${order.order_ID.split('-')[1]}</h5>
                    ${timeLeftHtml}
                </div>
                <p class="card-text mb-1">
                    <strong>Shop:</strong> ${order.shop_ID}
                </p>
                <p class="card-text mb-1">
                    <strong>Items:</strong> ${order.items_summary}
                </p>
                <p class="card-text mb-3">
                    <strong>Placed:</strong> ${new Date(order.order_time).toLocaleTimeString()}
                </p>
                <div class="mt-auto pt-2 border-top">
                    <span class="badge ${order.status === 'Ready' ? 'bg-success' : 'bg-warning'} status-badge">${order.status.toUpperCase()}</span>
                    <button class="btn btn-sm btn-success float-end btn-mark-ready" 
                            data-order-id="${order.order_ID}" 
                            data-prep-id="${order.prep_ID}"
                            ${buttonDisabled}>
                        ${buttonText}
                    </button>
                </div>
            </div>
        </div>
    `;
    return cardContainer;
}

async function markOrderAsReady(orderId, prepId, buttonElement) {
    buttonElement.disabled = true;
    buttonElement.textContent = 'Updating...';

    try {
        const response = await fetch(`/api/admin/order-ready/${orderId}/${prepId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (response.ok && result.status === 'Success') {
            showToast('success', `Order ${orderId.split('-')[1]} marked ready! Customer will be notified.`);
            
            // Optimistic UI update: change button to disabled "Ready"
            buttonElement.textContent = 'Ready for Pickup';
            buttonElement.classList.remove('btn-success');
            buttonElement.classList.add('btn-secondary');
            
            // Visually mark the card as ready without waiting for full refresh
            const orderCard = buttonElement.closest('.order-card');
            if (orderCard) {
                orderCard.classList.add('order-card-ready', 'border-success');
                orderCard.classList.remove('border-warning');
            }

            // A full refresh will eventually clean it up or keep it visually ready
            // fetchActiveOrders(); 

        } else {
            showToast('danger', `Failed to update order ${orderId.split('-')[1]}: ${result.message}`);
            buttonElement.disabled = false;
            buttonElement.textContent = 'Mark Ready (Trigger Notification)';
        }

    } catch (error) {
        console.error('Error updating order status:', error);
        showToast('danger', `Network error. Could not update order ${orderId.split('-')[1]}.`);
        buttonElement.disabled = false;
        buttonElement.textContent = 'Mark Ready (Trigger Notification)';
    }
}