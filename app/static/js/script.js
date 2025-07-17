// Global variables
let currentQuery = '';
let currentPage = 1;
let currentPageSize = 10;
let totalPages = 0;
let queryId = generateUUID();
let feedbackList = [];

// DOM elements
const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('query');
const countryCodeSelect = document.getElementById('countryCode');
const dateFromInput = document.getElementById('dateFrom');
const dateToInput = document.getElementById('dateTo');
const searchResults = document.getElementById('searchResults');
const noResults = document.getElementById('noResults');
const searchError = document.getElementById('searchError');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsTable = document.getElementById('resultsTable');
const pagination = document.getElementById('pagination');
const resultSummary = document.getElementById('resultSummary');
const pageSizeSelect = document.getElementById('pageSize');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Search form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentPage = 1;
        searchTenders();
    });
    
    // Page size change
    pageSizeSelect.addEventListener('change', function() {
        currentPageSize = parseInt(this.value);
        currentPage = 1;
        searchTenders();
    });
});

// Generate a UUID for query tracking
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Search tenders
function searchTenders() {
    // Get form values
    const query = queryInput.value.trim();
    const countryCode = countryCodeSelect.value;
    const dateFrom = dateFromInput.value;
    const dateTo = dateToInput.value;
    
    // Validate query
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    // If it's a new query, generate a new ID
    if (query !== currentQuery) {
        queryId = generateUUID();
        currentQuery = query;
        feedbackList = [];
    }
    
    // Prepare request data
    const requestData = {
        query: query,
        result_columns: [
            'ID', 
            'eTitle', 
            'eDescription', 
            'ePublisherCountryName', 
            'ePublicationDate', 
            'eDeadlineDate'
        ],
        page: currentPage,
        page_size: currentPageSize
    };
    
    // Add optional filters
    if (countryCode) {
        requestData.country_code = countryCode;
    }
    
    if (dateFrom) {
        requestData.date_from = dateFrom;
    }
    
    if (dateTo) {
        requestData.date_to = dateTo;
    }
    
    // Show loading indicator
    showLoading();
    
    // Send request to API
    fetch('/tenders_search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer T#nde0o43kl^4opkSD'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        displayResults(data);
    })
    .catch(error => {
        hideLoading();
        showError(error.message);
    });
}

// Display search results
function displayResults(data) {
    // Get results data
    const tenders = data.tenders;
    const pagination_data = data.pagination;
    
    // Update global variables
    totalPages = pagination_data.total_pages;
    
    // Clear previous results
    resultsTable.innerHTML = '';
    
    // Check if we have results
    if (tenders.length === 0) {
        showNoResults();
        return;
    }
    
    // Display results
    showResults();
    
    // Update result summary
    resultSummary.textContent = `Showing ${tenders.length} of ${pagination_data.total_results} results`;
    
    // Add tender rows
    tenders.forEach(tender => {
        const row = document.createElement('tr');
        
        // Format dates
        const pubDate = new Date(tender.ePublicationDate);
        const formattedPubDate = pubDate.toLocaleDateString();
        
        let formattedDeadline = 'N/A';
        if (tender.eDeadlineDate) {
            const deadlineDate = new Date(tender.eDeadlineDate);
            formattedDeadline = deadlineDate.toLocaleDateString();
        }
        
        // Create row content
        row.innerHTML = `
            <td>
                <div class="tender-title">${tender.eTitle}</div>
                <div class="small text-muted">${tender.ID}</div>
            </td>
            <td>${tender.ePublisherCountryName || 'N/A'}</td>
            <td>${formattedPubDate}</td>
            <td>${formattedDeadline}</td>
            <td>
                <div class="d-flex">
                    <button type="button" class="btn btn-sm feedback-btn feedback-btn-positive" 
                        title="Mark as relevant" onclick="provideFeedback('${tender.ID}', 'positive')">
                        <i class="bi bi-hand-thumbs-up-fill">👍</i>
                    </button>
                    <button type="button" class="btn btn-sm feedback-btn feedback-btn-negative" 
                        title="Mark as irrelevant" onclick="provideFeedback('${tender.ID}', 'negative')">
                        <i class="bi bi-hand-thumbs-down-fill">👎</i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-primary ms-2" 
                        title="View details" onclick="viewTenderDetails('${tender.ID}')">
                        Details
                    </button>
                </div>
            </td>
        `;
        
        resultsTable.appendChild(row);
    });
    
    // Update pagination
    updatePagination(pagination_data);
}

// Update pagination controls
function updatePagination(pagination_data) {
    pagination.innerHTML = '';
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    const prevLink = document.createElement('a');
    prevLink.className = 'page-link';
    prevLink.href = '#';
    prevLink.textContent = 'Previous';
    prevLink.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            searchTenders();
        }
    });
    prevLi.appendChild(prevLink);
    pagination.appendChild(prevLi);
    
    // Page numbers
    const totalPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(totalPagesToShow / 2));
    let endPage = Math.min(pagination_data.total_pages, startPage + totalPagesToShow - 1);
    
    if (endPage - startPage < totalPagesToShow - 1) {
        startPage = Math.max(1, endPage - totalPagesToShow + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
        const pageLink = document.createElement('a');
        pageLink.className = 'page-link';
        pageLink.href = '#';
        pageLink.textContent = i;
        pageLink.addEventListener('click', function(e) {
            e.preventDefault();
            currentPage = i;
            searchTenders();
        });
        pageLi.appendChild(pageLink);
        pagination.appendChild(pageLi);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === pagination_data.total_pages ? 'disabled' : ''}`;
    const nextLink = document.createElement('a');
    nextLink.className = 'page-link';
    nextLink.href = '#';
    nextLink.textContent = 'Next';
    nextLink.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentPage < pagination_data.total_pages) {
            currentPage++;
            searchTenders();
        }
    });
    nextLi.appendChild(nextLink);
    pagination.appendChild(nextLi);
}

// Provide feedback on a tender
function provideFeedback(tenderId, feedbackValue) {
    // Check if we already gave feedback for this tender
    const existingIndex = feedbackList.findIndex(item => item.ID === tenderId);
    
    if (existingIndex !== -1) {
        // Update existing feedback
        feedbackList[existingIndex].feedback = feedbackValue;
    } else {
        // Add new feedback
        feedbackList.push({
            ID: tenderId,
            feedback: feedbackValue
        });
    }
    
    // If we have at least 3 feedback items, send them to the server
    if (feedbackList.length >= 3) {
        submitFeedback();
    }
    
    // Visual feedback
    const button = event.target.closest('button');
    button.classList.add('active');
    setTimeout(() => {
        button.classList.remove('active');
    }, 500);
}

// Submit feedback to the server
function submitFeedback() {
    if (feedbackList.length === 0) {
        return;
    }
    
    const requestData = {
        query_id: queryId,
        search_query: currentQuery,
        feedback_list: feedbackList
    };
    
    fetch('/customer_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer T#nde0o43kl^4opkSD'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Feedback submitted successfully');
        // Clear the feedback list after submission
        feedbackList = [];
    })
    .catch(error => {
        console.error('Error submitting feedback:', error);
    });
}

// View tender details
function viewTenderDetails(tenderId) {
    // This function would normally fetch and display detailed info for a tender
    alert(`Viewing details for tender ${tenderId}`);
    // In a real application, you might show a modal with complete tender information
}

// Show/hide UI elements
function showLoading() {
    loadingIndicator.classList.remove('d-none');
    searchResults.classList.add('d-none');
    noResults.classList.add('d-none');
    searchError.classList.add('d-none');
}

function hideLoading() {
    loadingIndicator.classList.add('d-none');
}

function showResults() {
    searchResults.classList.remove('d-none');
    noResults.classList.add('d-none');
    searchError.classList.add('d-none');
}

function showNoResults() {
    searchResults.classList.add('d-none');
    noResults.classList.remove('d-none');
    searchError.classList.add('d-none');
}

function showError(message) {
    searchError.textContent = `Error: ${message}`;
    searchResults.classList.add('d-none');
    noResults.classList.add('d-none');
    searchError.classList.remove('d-none');
} 