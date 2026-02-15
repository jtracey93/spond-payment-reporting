// Spond Payment Reporting - Web App
// Author: GitHub Copilot
// This app replicates the Python tool's functionality in the browser

// Global state
const state = {
    bearerToken: null,
    clubId: null,
    members: [],
    memberMap: {},
    payments: [],
    granularData: [],
    summaryData: [],
    currentView: 'granular',
    sortColumn: null,
    sortDirection: 'asc',
    searchFilter: ''
};

// API Base URL
const API_BASE_URL = 'https://api.spond.com';

// DOM Elements
const elements = {
    bearerTokenInput: document.getElementById('bearer-token'),
    clubIdInput: document.getElementById('club-id'),
    toggleTokenBtn: document.getElementById('toggle-token-visibility'),
    fetchClubsBtn: document.getElementById('fetch-clubs-btn'),
    clubsList: document.getElementById('clubs-list'),
    loadDataBtn: document.getElementById('load-data-btn'),
    authStatus: document.getElementById('auth-status'),
    showInstructionsLink: document.getElementById('show-instructions'),
    tokenInstructions: document.getElementById('token-instructions'),
    filtersSection: document.getElementById('filters-section'),
    dataSection: document.getElementById('data-section'),
    loading: document.getElementById('loading'),
    errorMessage: document.getElementById('error-message'),
    searchFilter: document.getElementById('search-filter'),
    sortBy: document.getElementById('sort-by'),
    viewType: document.getElementById('view-type'),
    stats: document.getElementById('stats'),
    tableHeader: document.getElementById('table-header'),
    tableBody: document.getElementById('table-body'),
    exportCsvBtn: document.getElementById('export-csv-btn'),
    exportExcelBtn: document.getElementById('export-excel-btn'),
    exportPdfBtn: document.getElementById('export-pdf-btn')
};

// Event Listeners
function initEventListeners() {
    elements.toggleTokenBtn.addEventListener('click', toggleTokenVisibility);
    elements.showInstructionsLink.addEventListener('click', (e) => {
        e.preventDefault();
        elements.tokenInstructions.classList.toggle('hidden');
    });
    
    elements.bearerTokenInput.addEventListener('input', updateLoadButtonState);
    elements.clubIdInput.addEventListener('input', updateLoadButtonState);
    
    elements.fetchClubsBtn.addEventListener('click', fetchClubs);
    elements.loadDataBtn.addEventListener('click', loadPaymentData);
    
    elements.searchFilter.addEventListener('input', applyFilters);
    elements.sortBy.addEventListener('change', applySorting);
    elements.viewType.addEventListener('change', switchView);
    
    elements.exportCsvBtn.addEventListener('click', exportToCSV);
    elements.exportExcelBtn.addEventListener('click', exportToExcel);
    elements.exportPdfBtn.addEventListener('click', exportToPDF);
}

// Toggle token visibility
function toggleTokenVisibility() {
    const input = elements.bearerTokenInput;
    const btn = elements.toggleTokenBtn;
    
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Hide';
    } else {
        input.type = 'password';
        btn.textContent = 'Show';
    }
}

// Update load button state
function updateLoadButtonState() {
    const token = elements.bearerTokenInput.value.trim();
    const clubId = elements.clubIdInput.value.trim();
    
    elements.loadDataBtn.disabled = !(token && clubId);
}

// API Functions
async function makeApiRequest(endpoint, method = 'GET') {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'accept': 'application/json',
        'authorization': `Bearer ${state.bearerToken}`,
        'content-type': 'application/json'
    };
    
    if (state.clubId) {
        headers['x-spond-clubid'] = state.clubId;
    }
    
    try {
        const response = await fetch(url, {
            method,
            headers,
            mode: 'cors'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Fetch available clubs
async function fetchClubs() {
    const token = elements.bearerTokenInput.value.trim();
    
    if (!token) {
        showError('Please enter a bearer token first');
        return;
    }
    
    state.bearerToken = token;
    state.clubId = null; // Temporarily remove club ID for fetching clubs
    
    try {
        showStatus('Fetching clubs...', 'info');
        const clubs = await makeApiRequest('/club/v1/clubs');
        
        if (!clubs || clubs.length === 0) {
            showError('No clubs found for this token');
            return;
        }
        
        displayClubs(clubs);
        showStatus(`Found ${clubs.length} club(s)`, 'success');
    } catch (error) {
        showError(`Failed to fetch clubs: ${error.message}`);
    }
}

// Display available clubs
function displayClubs(clubs) {
    elements.clubsList.innerHTML = '';
    elements.clubsList.classList.remove('hidden');
    
    clubs.forEach(club => {
        const clubItem = document.createElement('div');
        clubItem.className = 'club-item';
        clubItem.innerHTML = `
            <div class="club-name">${club.name || 'Unnamed Club'}</div>
            <div class="club-id">${club.id}</div>
        `;
        
        clubItem.addEventListener('click', () => {
            // Remove selected class from all items
            document.querySelectorAll('.club-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            // Add selected class to clicked item
            clubItem.classList.add('selected');
            
            // Set club ID
            elements.clubIdInput.value = club.id;
            updateLoadButtonState();
        });
        
        elements.clubsList.appendChild(clubItem);
    });
}

// Load payment data
async function loadPaymentData() {
    state.bearerToken = elements.bearerTokenInput.value.trim();
    state.clubId = elements.clubIdInput.value.trim();
    
    showLoading(true);
    hideError();
    
    try {
        // Fetch members
        showStatus('Fetching members...', 'info');
        const members = await makeApiRequest('/club/v1/members?');
        state.members = members;
        
        // Build member map
        state.memberMap = {};
        members.forEach(member => {
            const memberId = member.id;
            const name = member.name || `${member.firstName || ''} ${member.lastName || ''}`.trim();
            if (memberId && name) {
                state.memberMap[memberId] = name;
            }
        });
        
        // Fetch payments
        showStatus('Fetching payments...', 'info');
        const payments = await makeApiRequest('/club/v1/payments/?');
        state.payments = payments;
        
        // Process payment data
        showStatus('Processing payment data...', 'info');
        await processPaymentData();
        
        // Show sections
        elements.filtersSection.classList.remove('hidden');
        elements.dataSection.classList.remove('hidden');
        
        // Render table
        renderTable();
        
        showStatus('Data loaded successfully!', 'success');
    } catch (error) {
        showError(`Failed to load data: ${error.message}. Please check your bearer token and club ID.`);
    } finally {
        showLoading(false);
    }
}

// Process payment data (similar to Python code)
async function processPaymentData() {
    state.granularData = [];
    
    for (const payment of state.payments) {
        const paymentId = payment.id;
        const paymentName = payment.title || 'Unnamed Payment';
        
        try {
            // Fetch payment details
            const details = await makeApiRequest(
                `/club/v1/payments/${paymentId}?includeSignupRequestRecipients=false`
            );
            const recipients = details.recipients || [];
            
            for (const recipient of recipients) {
                const status = recipient.status || '';
                
                // Only include unpaid recipients (UNANSWERED)
                if (status === 'UNANSWERED') {
                    const memberId = recipient.memberId;
                    const memberName = state.memberMap[memberId] || `Unknown (${memberId})`;
                    
                    // Extract amount
                    let amountPence = 0;
                    const claims = recipient.claims || [];
                    if (claims.length > 0) {
                        const products = claims[0].products || [];
                        if (products.length > 0) {
                            amountPence = products[0].price || 0;
                        }
                    }
                    
                    const amount = amountPence / 100.0; // Convert to pounds/dollars
                    const currency = recipient.currency || 'GBP';
                    
                    state.granularData.push({
                        memberName,
                        memberId,
                        paymentName,
                        paymentId,
                        amount,
                        currency,
                        status
                    });
                }
            }
        } catch (error) {
            console.warn(`Failed to process payment '${paymentName}':`, error);
        }
    }
    
    // Generate summary data
    generateSummaryData();
}

// Generate summary data (aggregated by member)
function generateSummaryData() {
    const summaryMap = {};
    
    state.granularData.forEach(row => {
        const key = `${row.memberId}_${row.currency}`;
        
        if (!summaryMap[key]) {
            summaryMap[key] = {
                memberName: row.memberName,
                memberId: row.memberId,
                currency: row.currency,
                totalAmount: 0,
                paymentCount: 0
            };
        }
        
        summaryMap[key].totalAmount += row.amount;
        summaryMap[key].paymentCount += 1;
    });
    
    state.summaryData = Object.values(summaryMap);
}

// Switch between granular and summary view
function switchView() {
    state.currentView = elements.viewType.value;
    renderTable();
}

// Apply filters
function applyFilters() {
    state.searchFilter = elements.searchFilter.value.toLowerCase();
    renderTable();
}

// Apply sorting
function applySorting() {
    const sortValue = elements.sortBy.value;
    const [column, direction] = sortValue.split('-');
    
    state.sortColumn = column;
    state.sortDirection = direction;
    
    renderTable();
}

// Get filtered and sorted data
function getFilteredData() {
    let data = state.currentView === 'granular' ? [...state.granularData] : [...state.summaryData];
    
    // Apply search filter
    if (state.searchFilter) {
        data = data.filter(row => {
            const searchText = state.searchFilter;
            return (
                row.memberName.toLowerCase().includes(searchText) ||
                (row.paymentName && row.paymentName.toLowerCase().includes(searchText)) ||
                row.currency.toLowerCase().includes(searchText)
            );
        });
    }
    
    // Apply sorting
    if (state.sortColumn) {
        data.sort((a, b) => {
            let aVal, bVal;
            
            switch (state.sortColumn) {
                case 'member':
                    aVal = a.memberName;
                    bVal = b.memberName;
                    break;
                case 'amount':
                    aVal = state.currentView === 'granular' ? a.amount : a.totalAmount;
                    bVal = state.currentView === 'granular' ? b.amount : b.totalAmount;
                    break;
                case 'payment':
                    aVal = a.paymentName || '';
                    bVal = b.paymentName || '';
                    break;
                default:
                    return 0;
            }
            
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            if (state.sortDirection === 'desc') {
                return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            } else {
                return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
            }
        });
    }
    
    return data;
}

// Render table
function renderTable() {
    const data = getFilteredData();
    
    // Update stats
    updateStats(data);
    
    // Render table header
    if (state.currentView === 'granular') {
        elements.tableHeader.innerHTML = `
            <tr>
                <th>Member Name</th>
                <th>Payment Name</th>
                <th class="currency-cell">Amount Owed</th>
                <th>Currency</th>
            </tr>
        `;
    } else {
        elements.tableHeader.innerHTML = `
            <tr>
                <th>Member Name</th>
                <th class="currency-cell">Total Amount Owed</th>
                <th>Currency</th>
                <th>Number of Payments</th>
            </tr>
        `;
    }
    
    // Render table body
    elements.tableBody.innerHTML = '';
    
    if (data.length === 0) {
        elements.tableBody.innerHTML = `
            <tr>
                <td colspan="${state.currentView === 'granular' ? 4 : 4}" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No data to display
                </td>
            </tr>
        `;
        return;
    }
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        
        if (state.currentView === 'granular') {
            tr.innerHTML = `
                <td>${row.memberName}</td>
                <td>${row.paymentName}</td>
                <td class="currency-cell">${formatCurrency(row.amount)}</td>
                <td>${row.currency}</td>
            `;
        } else {
            tr.innerHTML = `
                <td>${row.memberName}</td>
                <td class="currency-cell">${formatCurrency(row.totalAmount)}</td>
                <td>${row.currency}</td>
                <td>${row.paymentCount}</td>
            `;
        }
        
        elements.tableBody.appendChild(tr);
    });
}

// Update statistics
function updateStats(filteredData) {
    const totalItems = state.currentView === 'granular' ? 
        state.granularData.length : 
        state.summaryData.length;
    
    const filteredItems = filteredData.length;
    
    let totalAmount = 0;
    if (state.currentView === 'granular') {
        totalAmount = state.granularData.reduce((sum, row) => sum + row.amount, 0);
    } else {
        totalAmount = state.summaryData.reduce((sum, row) => sum + row.totalAmount, 0);
    }
    
    elements.stats.innerHTML = `
        <div>Total Items: <span>${totalItems}</span></div>
        <div>Filtered Items: <span>${filteredItems}</span></div>
        <div>Total Amount: <span>${formatCurrency(totalAmount)}</span></div>
        <div>Members: <span>${state.members.length}</span></div>
        <div>Payments: <span>${state.payments.length}</span></div>
    `;
}

// Format currency
function formatCurrency(amount) {
    return amount.toFixed(2);
}

// Export to CSV
function exportToCSV() {
    const data = getFilteredData();
    
    if (data.length === 0) {
        alert('No data to export');
        return;
    }
    
    let csv;
    
    if (state.currentView === 'granular') {
        csv = 'Member Name,Payment Name,Amount Owed,Currency\n';
        data.forEach(row => {
            csv += `"${row.memberName}","${row.paymentName}",${row.amount},${row.currency}\n`;
        });
    } else {
        csv = 'Member Name,Total Amount Owed,Currency,Number of Payments\n';
        data.forEach(row => {
            csv += `"${row.memberName}",${row.totalAmount},${row.currency},${row.paymentCount}\n`;
        });
    }
    
    downloadFile(csv, 'spond_payment_report.csv', 'text/csv');
}

// Export to Excel (using CSV format with .xlsx extension for simplicity)
function exportToExcel() {
    const data = getFilteredData();
    
    if (data.length === 0) {
        alert('No data to export');
        return;
    }
    
    // For a true Excel export, we'd need a library like SheetJS
    // For simplicity, we'll export as CSV with .xlsx extension
    // Users can open in Excel and save as proper xlsx if needed
    
    let csv;
    
    if (state.currentView === 'granular') {
        csv = 'Member Name\tPayment Name\tAmount Owed\tCurrency\n';
        data.forEach(row => {
            csv += `${row.memberName}\t${row.paymentName}\t${row.amount}\t${row.currency}\n`;
        });
    } else {
        csv = 'Member Name\tTotal Amount Owed\tCurrency\tNumber of Payments\n';
        data.forEach(row => {
            csv += `${row.memberName}\t${row.totalAmount}\t${row.currency}\t${row.paymentCount}\n`;
        });
    }
    
    downloadFile(csv, 'spond_payment_report.xls', 'application/vnd.ms-excel');
}

// Export to PDF
function exportToPDF() {
    alert('PDF export requires a print dialog. Please use your browser\'s Print function (Ctrl+P or Cmd+P) and select "Save as PDF".');
    window.print();
}

// Download file
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// UI Helper Functions
function showLoading(show) {
    elements.loading.classList.toggle('hidden', !show);
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.classList.remove('hidden');
}

function hideError() {
    elements.errorMessage.classList.add('hidden');
}

function showStatus(message, type) {
    elements.authStatus.textContent = message;
    elements.authStatus.className = `status-message ${type}`;
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    updateLoadButtonState();
});
