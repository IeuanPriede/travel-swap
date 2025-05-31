function handleMatch(profileId, liked) {
  console.log("Clicked Next for profile ID:", profileId);
  const url = liked === true ? '/like/' : '/next/';
  const bodyData = { profile_id: profileId };

  if (window.currentFilters && liked !== true) {
    // Only apply filters for Next, not Like
    bodyData.filters = Object.fromEntries(window.currentFilters.entries());
  }

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify(bodyData)
  })
  .then(response => {
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("Expected JSON, but got something else");
    }
    return response.json();
  })
  .then(data => {
    console.log("Server said:", JSON.stringify(data, null, 2));
    // Unified alert for both match and like
    if (data.message) {
      console.log("ALERT:", data.message);
      showMessageAlert(data.message, data.match ? 'success' : 'info');
    }
    console.log("New profile loaded:", profileId);
    document.getElementById('profile-section').innerHTML = data.next_profile_html;

    initManualImageViewer();
  })
  .catch(error => {
    console.error("Failed to load next profile:", error);
    alert("Oops! Something went wrong. Please try again.");
  });
}

// Helper to get CSRF token from cookie
function getCSRFToken() {
  let csrfToken = null;
  document.cookie.split(';').forEach(cookie => {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      csrfToken = decodeURIComponent(value);
    }
  });
  return csrfToken;
}

// Location: Country lists
$(document).ready(function () {
  const $select = $('#id_location');

  $select.select2({
    placeholder: 'Select a country',
    allowClear: true,
    dropdownParent: $('#edit-profile-form')  // ensures dropdown works inside modals/forms
  });

  // Fix upward opening: force dropdown to open below
  $select.on('select2:open', function () {
    setTimeout(() => {
      const container = $('.select2-container--open');
      const dropdown = $('.select2-dropdown');

      if (container.length && dropdown.length) {
        const height = container.outerHeight();
        dropdown.css({
          top: height + 'px',
          bottom: 'auto'
        });
      }
    }, 50);
  });
});

// Search filter AJAX
const filterForm = document.querySelector('#filter-form');
if (filterForm) {
  filterForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const url = this.getAttribute('action') || window.location.href;
    const formData = new FormData(this);

    const params = new URLSearchParams();
    for (const [key, value] of formData.entries()) {
      if (value) params.append(key, value);
    }

    fetch(`${url}?${params.toString()}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById('profile-section').innerHTML = data.next_profile_html;
        window.currentFilters = params;
      })
      .catch(error => {
        console.error('Search filter AJAX error:', error);
      });
  });
}

function initManualImageViewer() {
  const imageDataElement = document.getElementById('house-image-urls');
  if (!imageDataElement) return;

  const imageUrls = JSON.parse(imageDataElement.textContent);
  let currentImageIndex = 0;

  const imgElement = document.getElementById('current-house-image');
  const prevBtn = document.getElementById('prev-image');
  const nextBtn = document.getElementById('next-image');

  if (prevBtn && nextBtn && imgElement && imageUrls.length > 0) {
    prevBtn.addEventListener('click', () => {
      currentImageIndex = (currentImageIndex - 1 + imageUrls.length) % imageUrls.length;
      imgElement.src = imageUrls[currentImageIndex];
    });

    nextBtn.addEventListener('click', () => {
      currentImageIndex = (currentImageIndex + 1) % imageUrls.length;
      imgElement.src = imageUrls[currentImageIndex];
    });
  }
}

document.addEventListener("DOMContentLoaded", function () {
  console.log("🚀 DOM ready — init viewer");
  initManualImageViewer();
});

// Navbar fixed on scroll
document.addEventListener('DOMContentLoaded', function () {
  const navbar = document.querySelector('.navbar');

  // Handle scroll event
  window.addEventListener('scroll', function () {
    if (window.scrollY > 10) {
      navbar.classList.add('bg-primary');
    } else {
      navbar.classList.remove('bg-primary');
    }
  });
});

// Ensure correct navbar color on page load (after layout)
window.addEventListener('load', function () {
  const navbar = document.querySelector('.navbar');
  if (window.scrollY > 10 || document.body.scrollHeight <= window.innerHeight) {
    navbar.classList.add('bg-primary');
  }
});

// Alert message
// Define and expose globally
function showMessageAlert(msg, type = 'info') {
  const alertDiv = document.getElementById('message-feedback');
  if (!alertDiv) {
    console.warn('No #message-feedback container found.');
    return;
  }

  console.log(`Injecting alert: [${type}] ${msg}`);

  alertDiv.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">
      ${msg}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;

  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alertDiv.querySelector('.alert'));
    bsAlert.close();
  }, 5000);
}

// ✅ Now safely attach to global scope
window.showMessageAlert = showMessageAlert;
