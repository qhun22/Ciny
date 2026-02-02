// Profile Page JavaScript - QHUN22 Mobile

/**
 * Switch between profile tabs
 * @param {string} tab - Tab name to show
 */
function showTab(tab) {
    // Hide all tabs
    const tabs = ['overview', 'addresses', 'vouchers', 'orders', 'feedback'];
    tabs.forEach(t => {
        const tabEl = document.getElementById('tab-' + t);
        const btnEl = document.getElementById('btn-' + t);
        if (tabEl) tabEl.classList.add('hidden');
        if (btnEl) {
            btnEl.className = 'profile-tab-btn';
        }
    });
    
    // Show selected tab
    const selectedTab = document.getElementById('tab-' + tab);
    const selectedBtn = document.getElementById('btn-' + tab);
    if (selectedTab) selectedTab.classList.remove('hidden');
    if (selectedBtn) {
        selectedBtn.className = 'profile-tab-btn active';
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
        Swal.fire({
            title: 'Lỗi!',
            text: 'Vui lòng chọn một địa chỉ để xóa!',
            icon: 'error',
            confirmButtonColor: '#dc2626'
        });
        return;
    }
    
    showConfirmDialog('Xác nhận xóa địa chỉ', 'Bạn có chắc chắn muốn xóa địa chỉ này không?', 'warning')
        .then((result) => {
            if (result.isConfirmed) {
                document.getElementById('deleteAddressId').value = selectedRadio.value;
                document.getElementById('deleteForm').action = '/profile/address/delete/' + selectedRadio.value + '/';
                document.getElementById('deleteForm').submit();
            }
        });
}

/**
 * Delete a single voucher
 * @param {string} voucherId - Voucher ID to delete
 */
function deleteSingleVoucher(voucherId) {
    showConfirmDialog('Xác nhận xóa voucher', 'Bạn có chắc muốn xóa voucher này không?', 'warning')
        .then((result) => {
            if (result.isConfirmed) {
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
                            Swal.fire({
                                title: 'Thành công!',
                                text: data.message,
                                icon: 'success',
                                confirmButtonColor: '#16a34a'
                            }).then(() => location.reload());
                        } else {
                            Swal.fire({
                                title: 'Lỗi!',
                                text: data.message,
                                icon: 'error',
                                confirmButtonColor: '#dc2626'
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire({
                            title: 'Lỗi!',
                            text: 'Có lỗi xảy ra khi xóa voucher.',
                            icon: 'error',
                            confirmButtonColor: '#dc2626'
                        });
                    });
                }
            }
        });
}

/**
 * Set default address via AJAX
 * @param {number} addressId - Address ID to set as default
 */
function setDefaultAddress(addressId) {
    showConfirmDialog('Xác nhận đặt địa chỉ mặc định', 'Bạn có chắc muốn đặt địa chỉ này làm mặc định không?', 'info')
        .then((result) => {
            if (result.isConfirmed) {
                fetch('/profile/address/default/' + addressId + '/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        Swal.fire({
                            title: 'Thành công!',
                            text: 'Đã đặt địa chỉ mặc định.',
                            icon: 'success',
                            confirmButtonColor: '#16a34a'
                        }).then(() => location.reload());
                    }
                });
            }
        });
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

/**
 * Toggle all voucher checkboxes
 * @param {HTMLInputElement} checkbox - Master checkbox
 */
function toggleAllVouchers(checkbox) {
    const checkboxes = document.querySelectorAll('.voucher-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
}

/**
 * Show cancel order modal
 * @param {number} orderId - Order ID to cancel
 */
function showCancelModal(orderId) {
    const modal = document.getElementById('cancelOrderModal');
    const orderIdSpan = document.getElementById('cancelOrderId');
    const form = document.getElementById('cancelOrderForm');
    
    if (modal && orderIdSpan && form) {
        orderIdSpan.textContent = orderId;
        form.action = '/orders/' + orderId + '/cancel/';
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
}

/**
 * Hide cancel order modal
 */
function hideCancelModal() {
    const modal = document.getElementById('cancelOrderModal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = ''; // Restore scrolling
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved tab preference
    const savedTab = localStorage.getItem('profileTab');
    if (savedTab) {
        showTab(savedTab);
    }
});

