document.addEventListener('DOMContentLoaded', () => {
    // Check if the user is supposed to be here (Admin check is done in app.py login)
    // For this demo, we assume they reached this page after a successful Admin login.

    fetchInventoryStatus();
    fetchSalesReport();
});

/**
 * Fetches inventory status from the backend and renders the table.
 * Demonstrates the result of the CheckReorderLevel trigger.
 */
async function fetchInventoryStatus() {
    try {
        const response = await fetch('/api/admin/inventory');
        const inventoryData = await response.json();

        if (response.ok) {
            renderInventoryTable(inventoryData);
        } else {
            console.error('Failed to fetch inventory:', inventoryData.message);
            displayMessage('Failed to load inventory data.', 'inventory-table-body');
        }
    } catch (error) {
        console.error('Network error during inventory fetch:', error);
        displayMessage('Error connecting to server for inventory data.', 'inventory-table-body');
    }
}

/**
 * Renders the inventory data, highlighting items needing reorder.
 * @param {Array} data - Array of inventory objects from the API.
 */
function renderInventoryTable(data) {
    const tableBody = document.getElementById('inventory-table-body');
    tableBody.innerHTML = ''; // Clear previous content

    if (data.length === 0) {
        displayMessage('No inventory data available.', 'inventory-table-body');
        return;
    }

    data.forEach(item => {
        const row = document.createElement('tr');
        // Use the reorder_needed flag set in app.py to apply styling
        if (item.reorder_needed) {
            row.className = 'reorder-needed hover:bg-red-100';
        } else {
            row.className = 'hover:bg-gray-100';
        }

        const statusClass = item.reorder_needed ? 'bg-red-500 text-white' : 'bg-green-500 text-white';
        const statusText = item.reorder_needed ? 'REORDER URGENT' : 'OK';

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item.item_name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.shop_name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">${item.quantity} ${item.unit}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.reorder_level} ${item.unit}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
                    ${statusText}
                </span>
            </td>
        `;
        tableBody.appendChild(row);
    });
}


/**
 * Fetches sales report from the backend and renders the table.
 * Demonstrates the Complex Query (SUM, COUNT, GROUP BY).
 */
async function fetchSalesReport() {
    try {
        const response = await fetch('/api/admin/sales-report');
        const reportData = await response.json();

        if (response.ok) {
            renderSalesReportTable(reportData);
        } else {
            console.error('Failed to fetch sales report:', reportData.message);
            displayMessage('Failed to load sales report.', 'sales-report-table-body');
        }
    } catch (error) {
        console.error('Network error during sales report fetch:', error);
        displayMessage('Error connecting to server for sales report data.', 'sales-report-table-body');
    }
}

/**
 * Renders the sales report data.
 * @param {Array} data - Array of sales report objects from the API.
 */
function renderSalesReportTable(data) {
    const tableBody = document.getElementById('sales-report-table-body');
    tableBody.innerHTML = ''; // Clear previous content

    if (data.length === 0) {
        displayMessage('No sales data available.', 'sales-report-table-body');
        return;
    }

    let totalRevenue = 0;
    data.forEach(row => {
        totalRevenue += row.gross_revenue;

        const tableRow = document.createElement('tr');
        tableRow.className = 'hover:bg-gray-100';
        tableRow.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${row.shop_name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${row.total_orders}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${row.total_items_sold}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-700">₹ ${row.gross_revenue.toFixed(2)}</td>
        `;
        tableBody.appendChild(tableRow);
    });

    // Add a row for total gross revenue
    const totalRow = document.createElement('tr');
    totalRow.className = 'bg-gray-100 font-extrabold border-t-2 border-gray-300';
    totalRow.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap text-base text-gray-900">GRAND TOTAL</td>
        <td class="px-6 py-4 whitespace-nowrap"></td>
        <td class="px-6 py-4 whitespace-nowrap"></td>
        <td class="px-6 py-4 whitespace-nowrap text-base text-green-800">₹ ${totalRevenue.toFixed(2)}</td>
    `;
    tableBody.appendChild(totalRow);
}

/**
 * Helper function to display an error or informational message in a table.
 * @param {string} message - The message to display.
 * @param {string} tableBodyId - The ID of the table body element.
 */
function displayMessage(message, tableBodyId) {
    const tableBody = document.getElementById(tableBodyId);
    tableBody.innerHTML = `
        <tr>
            <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500 italic">
                ${message}
            </td>
        </tr>
    `;
}