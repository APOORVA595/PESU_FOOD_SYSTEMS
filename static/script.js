// static/script.js

const MENU_API_URL = '/api/menu';
const ORDER_API_URL = '/api/place_order';

const menuContainer = document.getElementById('menu-container');
const orderForm = document.getElementById('order-form');
const orderStatusDiv = document.getElementById('order-status');

/**
 * Task 2: Fetches menu data from the Integrator's API and displays it.
 */
async function loadMenu() {
    menuContainer.innerHTML = '<div class="col-12"><p class="text-info">Fetching menu...</p></div>';
    
    try {
        const response = await fetch(MENU_API_URL);
        const menuItems = await response.json(); 

        if (menuItems.length === 0) {
             menuContainer.innerHTML = '<div class="col-12"><p class="text-warning">No menu items found.</p></div>';
             return;
        }

        menuContainer.innerHTML = ''; // Clear the "Fetching" message
        
        menuItems.forEach(item => {
            // Assume the item object contains: item_ID, item_name, price, available (boolean)
            const isAvailable = item.available === true;
            const cardClass = isAvailable ? 'border-success' : 'border-danger';
            const buttonState = isAvailable ? '' : 'disabled';
            const buttonText = isAvailable ? 'Quantity:' : 'Out of Stock';

            const itemHtml = `
                <div class="col-md-4 mb-4">
                    <div class="card h-100 ${cardClass}">
                        <div class="card-body">
                            <h5 class="card-title text-dark">${item.item_name}</h5>
                            <p class="card-text text-muted">Price: **₹${item.price.toFixed(2)}**</p>
                            <div class="form-group">
                                <label for="qty-${item.item_ID}">${buttonText}</label>
                                <input type="number" 
                                       class="form-control item-qty" 
                                       id="qty-${item.item_ID}" 
                                       data-item-id="${item.item_ID}"
                                       min="0" value="0"
                                       ${buttonState}>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            menuContainer.innerHTML += itemHtml;
        });

    } catch (error) {
        console.error('Error fetching menu:', error);
        menuContainer.innerHTML = '<div class="col-12"><p class="text-danger">Could not load menu. Check server connection.</p></div>';
    }
}

/**
 * Task 3 & 4: Handles form submission, collects data, sends to API, and displays result.
 */
orderForm.addEventListener('submit', async function(event) {
    event.preventDefault(); 
    orderStatusDiv.classList.add('d-none'); // Hide previous status

    const items = [];
    let totalQuantity = 0; 
    
    // 1. Collect selected items
    document.querySelectorAll('.item-qty').forEach(input => {
        // Only include items that are not disabled and have a quantity > 0
        if (!input.disabled) {
            const qty = parseInt(input.value);
            if (qty > 0) {
                items.push({
                    item_id: input.dataset.itemId,
                    quantity: qty
                });
                totalQuantity += qty;
            }
        }
    });

    if (items.length === 0) {
        displayStatus('Please select at least one item to place an order.', 'alert-warning');
        return;
    }

    const orderData = {
        // Data from hidden inputs in index.html
        customer_id: document.getElementById('customer-id').value,
        shop_id: document.getElementById('shop-id').value,
        total_quantity: totalQuantity, // Needed for AddOrder Procedure
        items: items
    };

    // Temporarily disable button to prevent multiple submissions
    const submitButton = orderForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Processing...';

    // 2. Send data to Integrator's API
    try {
        const response = await fetch(ORDER_API_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(orderData)
        });

        const result = await response.json();
        
        // 3. Display Order Status (Task 4)
        if (response.ok && result.status === 'Success') {
            displayStatus(
                `🎉 Order ${result.order_id} Placed! **Total: ₹${result.total.toFixed(2)}**`, 
                'alert-success'
            );
            orderForm.reset(); // Clear quantities on success
            loadMenu(); // Refresh menu (in case inventory changed)
        } else {
            // Handle errors, including database constraint errors returned by Flask
            displayStatus(
                `Order Failed: ${result.message || 'An unknown server error occurred.'}`, 
                'alert-danger'
            );
        }

    } catch (error) {
        console.error('Submission failed:', error);
        displayStatus('Network error. Could not connect to the ordering system.', 'alert-danger');
    } finally {
        // Re-enable button
        submitButton.disabled = false;
        submitButton.textContent = '🛒 Place Order';
    }
});


/**
 * Helper function to update the status div.
 */
function displayStatus(message, className) {
    orderStatusDiv.className = `alert mt-4 ${className}`;
    orderStatusDiv.innerHTML = message;
    orderStatusDiv.classList.remove('d-none');
}

// Start the application by loading the menu
window.onload = loadMenu;