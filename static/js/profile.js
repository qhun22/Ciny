// Profile Page JavaScript - QHUN22 Mobile

/**
 * Switch between profile tabs
 * @param {string} tab - Tab name to show
 */
function showTab(tab) {
    // Hide all tabs
    const tabs = ['overview', 'addresses', 'vouchers'];
    tabs.forEach(t => {
        const tabEl = document.getElementById('tab-' + t);
        const btnEl = document.getElementById('btn-' + t);
        if (tabEl) tabEl.classList.add('hidden');
        if (btnEl) {
            btnEl.className = 'w-full text-left px-4 py-3 rounded-lg font-medium mb-2 transition-colors hover:bg-gray-50 text-gray-600';
        }
    });
    
    // Show selected tab
    const selectedTab = document.getElementById('tab-' + tab);
    const selectedBtn = document.getElementById('btn-' + tab);
    if (selectedTab) selectedTab.classList.remove('hidden');
    if (selectedBtn) {
        selectedBtn.className = 'w-full text-left px-4 py-3 rounded-lg font-medium mb-2 transition-colors bg-blue-600 text-white';
    }
    
    // Save preference to localStorage
    localStorage.setItem('profileTab', tab);
}

/**
 * Select an address (click on card also selects radio)
 * @param {number} addressId - Address ID to select
 */
function selectAddress(addressId) {
    const radio = document.getElementById('addr_' + addressId);
    if (radio) {
        radio.checked = true;
    }
}

/**
 * Delete selected address
 */
function deleteSelectedAddress() {
    const selectedRadio = document.querySelector('input[name="default_address"]:checked');
    if (!selectedRadio) {
        alert('Vui lòng chọn một địa chỉ để xóa!');
        return;
    }
    if (confirm('Xóa địa chỉ này?')) {
        document.getElementById('deleteAddressId').value = selectedRadio.value;
        document.getElementById('deleteForm').action = '/profile/address/delete/' + selectedRadio.value + '/';
        document.getElementById('deleteForm').submit();
    }
}

/**
 * Delete a single voucher
 * @param {string} voucherId - Voucher ID to delete
 */
function deleteSingleVoucher(voucherId) {
    if (confirm('Bạn có chắc muốn xóa voucher này?')) {
        const form = document.getElementById('deleteVouchersForm');
        if (form) {
            const formData = new FormData(form);
            formData.append('voucher_ids[]', voucherId);
            
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi xóa voucher.');
            });
        }
    }
}

/**
 * Set default address via AJAX
 * @param {number} addressId - Address ID to set as default
 */
function setDefaultAddress(addressId) {
    if (confirm('Đặt địa chỉ này làm mặc định?')) {
        fetch('/profile/address/default/' + addressId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) location.reload();
        });
    }
}

/**
 * Get cookie by name
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value or null
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved tab preference
    const savedTab = localStorage.getItem('profileTab');
    if (savedTab) {
        showTab(savedTab);
    }
});

