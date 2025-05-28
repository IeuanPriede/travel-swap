function handleMatch(profileId, liked) {
  console.log("Clicked Next for profile ID:", profileId);
  const url = liked === true ? '/like/' : '/next/';

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({ profile_id: profileId })
  })
  .then(response => {
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("Expected JSON, but got something else");
    }
    return response.json();
  })
  .then(data => {
    console.log("Server said:", data);
    if (data.match) {
      console.log("Server returned:", data);
      alert("🎉 It's a match with " + data.match_with + "!");
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
