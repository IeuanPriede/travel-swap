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
    console.log("Message from server:", data.message);
    // Unified alert for both match and like
    if (data.message) {
      console.log("ALERT:", data.message);
      alert(data.message);
    }
    document.getElementById('profile-section').innerHTML = data.next_profile_html;
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
document.querySelector('#filter-form').addEventListener('submit', function (e) {
  e.preventDefault();

  const form = this;
  const url = form.getAttribute('action') || window.location.href;
  const formData = new FormData(form);

  const params = new URLSearchParams();
  for (const [key, value] of formData.entries()) {
    if (value) params.append(key, value);
  }

  fetch(`${url}?${params.toString()}`, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById('profile-section').innerHTML = data.next_profile_html;

      // Save current filters in JS for reuse on "Next"
      window.currentFilters = params;
    })
    .catch(error => {
      console.error('Search filter AJAX error:', error);
    });
});
