/**
 * JavaScript cho PhoneShop
 * Xu ly cac chuc nang tuong tac tren trang web
 */

// Variables to store current selections
let currentStorage = '';
let currentColor = '';
let basePrice = 0;
let selectedStoragePrice = 0;

/**
 * Thay doi anh chinh khi click vao thumbnail
 */
function changeImage(imageUrl) {
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = imageUrl;
    }
}

/**
 * Chon tuyen chon bo nho - Cap nhat gia
 */
function selectStorage(button, storage, price) {
    // Update UI
    const buttons = document.querySelectorAll('.storage-btn');
    buttons.forEach(btn => {
        btn.classList.remove('border-primary', 'bg-blue-50');
        btn.classList.add('border-gray-200');
    });
    button.classList.remove('border-gray-200');
    button.classList.add('border-primary', 'bg-blue-50');
    
    // Save selection
    currentStorage = storage;
    selectedStoragePrice = parseFloat(price) || 0;
    
    // Update price display
    updatePriceDisplay(storage);
}

/**
 * Cap nhat hien thi gia khi chon bo nho
 */
function updatePriceDisplay(selectedStorage) {
    const priceElement = document.getElementById('currentPrice');
    const storageInfo = document.getElementById('selectedStorage');
    
    // Lay gia base tu template (duoc gan khi trang load)
    if (window.productBasePrice) {
        basePrice = window.productBasePrice;
    }
    
    if (priceElement && basePrice > 0) {
        const newPrice = basePrice + selectedStoragePrice;
        priceElement.textContent = newPrice.toLocaleString('vi-VN') + 'đ';
    }
    
    if (storageInfo && selectedStorage) {
        storageInfo.textContent = selectedStorage;
    }
}

/**
 * Chon tuyen chon mau sac
 */
function selectColor(button, color, imageUrl) {
    // Update UI
    const buttons = document.querySelectorAll('.color-btn');
    buttons.forEach(btn => {
        btn.classList.remove('border-primary', 'bg-blue-50');
        btn.classList.add('border-gray-200');
    });
    button.classList.remove('border-gray-200');
    button.classList.add('border-primary', 'bg-blue-50');
    
    // Save selection
    currentColor = color;
    
    // Change main image if imageUrl provided
    if (imageUrl) {
        changeImage(imageUrl);
    }
}

/**
 * Them dong moi cho tuy chon bo nho (Admin page)
 */
function addStorageRow() {
    const container = document.getElementById('storageContainer');
    if (!container) return;
    
    const newRow = document.createElement('div');
    newRow.className = 'flex gap-3 storage-row';
    newRow.innerHTML = `
        <input type="text" name="storage_name[]" placeholder="Vi du: 256GB"
               class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-primary">
        <input type="number" name="storage_price[]" placeholder="Gia them (0 neu khong co)"
               min="0" value="0"
               class="w-48 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-primary">
        <button type="button" onclick="removeRow(this)"
                class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition">
            -
        </button>
    `;
    
    container.appendChild(newRow);
}

/**
 * Them dong moi cho tuy chon mau sac (Admin page)
 */
function addColorRow() {
    const container = document.getElementById('colorContainer');
    if (!container) return;
    
    const newRow = document.createElement('div');
    newRow.className = 'flex gap-3 color-row';
    newRow.innerHTML = `
        <input type="text" name="color_name[]" placeholder="Vi du: Starlight"
               class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-primary">
        <input type="file" name="color_image[]" accept="image/*"
               class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-primary">
        <button type="button" onclick="removeRow(this)"
                class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition">
            -
        </button>
    `;
    
    container.appendChild(newRow);
}

/**
 * Xoa mot dong (Admin page)
 */
function removeRow(button) {
    const row = button.closest('.storage-row, .color-row');
    if (row) {
        row.remove();
    }
}

/**
 * Xu ly form ma giam gia
 */
function setupCouponForm() {
    const couponForm = document.getElementById('couponForm');
    if (!couponForm) return;
    
    couponForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const couponCode = document.getElementById('couponCode').value.trim();
        const messageElement = document.getElementById('couponMessage');
        
        if (!couponCode) {
            if (messageElement) {
                messageElement.textContent = 'Vui long nhap ma giam gia';
                messageElement.className = 'text-sm mt-2 text-red-600';
                messageElement.classList.remove('hidden');
            }
            return;
        }
        
        // Get product_id from URL
        const pathParts = window.location.pathname.split('/');
        const productId = pathParts[pathParts.indexOf('product') + 1];
        
        // Send AJAX request
        fetch('/product/' + productId + '/coupon/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: 'code=' + encodeURIComponent(couponCode)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                updatePriceWithCoupon(data.final_price, data.discount_percent);
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Co loi xay ra. Vui long thu lai.', 'error');
        });
    });
}

/**
 * Hien thi thong bao
 */
function showMessage(message, type) {
    const messageElement = document.getElementById('couponMessage');
    if (messageElement) {
        messageElement.textContent = message;
        messageElement.className = 'text-sm mt-2 ' + (type === 'success' ? 'text-green-600' : 'text-red-600');
        messageElement.classList.remove('hidden');
    }
}

/**
 * Cap nhat gia sau khi ap dung ma giam gia
 */
function updatePriceWithCoupon(finalPrice, discountPercent) {
    const priceContainer = document.querySelector('.bg-gray-100');
    if (priceContainer) {
        const newHtml = '<div class="flex items-center gap-3 mb-2">' +
            '<span class="text-gray-400 line-through text-lg" id="originalDisplay"></span>' +
            '<span class="text-red-600 text-3xl font-bold" id="currentPrice">' + parseInt(finalPrice).toLocaleString() + ' đ</span>' +
            '<span class="bg-red-500 text-white px-2 py-1 rounded text-sm font-bold">-' + discountPercent + '%</span>' +
            '</div>' +
            '<p class="text-green-600 text-sm">Da ap dung ma giam gia!</p>';
        priceContainer.innerHTML = newHtml;
    }
}

/**
 * Lay gia tri cookie
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
 * Xu ly gallery anh - click de doi anh chinh
 */
function initGallery() {
    const thumbnails = document.querySelectorAll('[onclick*="changeImage"]');
    thumbnails.forEach(function(thumb) {
        thumb.addEventListener('click', function(e) {
            e.preventDefault();
            
            const onclickAttr = this.getAttribute('onclick');
            const match = onclickAttr.match(/changeImage\(['"]([^'"]+)['"]\)/);
            if (match && match[1]) {
                changeImage(match[1]);
            }
            
            thumbnails.forEach(function(t) {
                t.classList.remove('border-primary');
                t.classList.add('border-gray-200');
            });
            this.classList.remove('border-gray-200');
            this.classList.add('border-primary');
        });
    });
}

/**
 * Format so tien thanh dinh dang đ
 */
function formatCurrency(amount) {
    return amount.toLocaleString('vi-VN') + 'đ';
}

// Initialize when page is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize gallery
    initGallery();
    
    // Initialize coupon form
    setupCouponForm();
    
    // Lay gia sale cua san pham tu template
    const priceElement = document.querySelector('#currentPrice');
    if (priceElement) {
        const priceText = priceElement.textContent.replace(/[^\d]/g, '');
        window.productBasePrice = parseInt(priceText) || 0;
        basePrice = window.productBasePrice;
    }
});
